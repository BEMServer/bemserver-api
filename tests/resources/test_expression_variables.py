"""Expression variables tests"""

import pytest

from tests.common import AuthHeader

DUMMY_ID = 69

EXPRESSION_VARIABLES_URL = "/expression_variables/"


class TestExpressionVariablesApi:
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_expression_variables_api(
        self, app, users, campaign_scopes, timeseries, expressions
    ):
        creds = users["Chuck"]["creds"]
        cs_1_id = campaign_scopes[0]
        cs_2_id = campaign_scopes[1]
        ts_1_id = timeseries[0]  # in cs_1
        ts_2_id = timeseries[1]  # in cs_2
        ts_3_id = timeseries[2]  # in cs_1
        ts_4_id = timeseries[3]  # in cs_2
        expr_1_id = expressions[0]  # in cs_1, output=ts_1
        expr_2_id = expressions[1]  # in cs_2, output=ts_2

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(EXPRESSION_VARIABLES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST (aggregation defaults to "avg")
            var_1 = {
                "campaign_scope_id": cs_1_id,
                "expression_id": expr_1_id,
                "name": "x",
                "timeseries_id": ts_3_id,
            }
            ret = client.post(EXPRESSION_VARIABLES_URL, json=var_1)
            assert ret.status_code == 201
            ret_val = ret.json
            var_1_id = ret_val.pop("id")
            var_1_etag = ret.headers["ETag"]
            assert ret_val["aggregation"] == "avg"
            assert ret_val["campaign_scope_id"] == cs_1_id
            assert ret_val["expression_id"] == expr_1_id
            assert ret_val["name"] == "x"
            assert ret_val["timeseries_id"] == ts_3_id

            # POST violating unique (expression_id, name)
            ret = client.post(EXPRESSION_VARIABLES_URL, json=var_1)
            assert ret.status_code == 409

            # POST with timeseries in wrong campaign scope
            var_bad_ts_scope = {
                "campaign_scope_id": cs_1_id,
                "expression_id": expr_1_id,
                "name": "y",
                "timeseries_id": ts_2_id,  # ts_2 is in cs_2
            }
            ret = client.post(EXPRESSION_VARIABLES_URL, json=var_bad_ts_scope)
            assert ret.status_code == 422
            assert "_schema" in ret.json["errors"]["json"]

            # POST with expression in wrong campaign scope
            var_bad_expr_scope = {
                "campaign_scope_id": cs_2_id,
                "expression_id": expr_1_id,  # expr_1 is in cs_1
                "name": "y",
                "timeseries_id": ts_4_id,
            }
            ret = client.post(EXPRESSION_VARIABLES_URL, json=var_bad_expr_scope)
            assert ret.status_code == 422
            assert "_schema" in ret.json["errors"]["json"]

            # POST non-existent timeseries_id -> 409
            ret = client.post(
                EXPRESSION_VARIABLES_URL,
                json={
                    "campaign_scope_id": cs_1_id,
                    "expression_id": expr_1_id,
                    "name": "z",
                    "timeseries_id": DUMMY_ID,
                },
            )
            assert ret.status_code == 409

            # POST non-existent expression_id -> 409
            ret = client.post(
                EXPRESSION_VARIABLES_URL,
                json={
                    "campaign_scope_id": cs_1_id,
                    "expression_id": DUMMY_ID,
                    "name": "z",
                    "timeseries_id": ts_3_id,
                },
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(EXPRESSION_VARIABLES_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert ret.json[0]["id"] == var_1_id

            # GET by id
            ret = client.get(f"{EXPRESSION_VARIABLES_URL}{var_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == var_1_etag

            # PUT (change aggregation and timeseries)
            var_1_put = {
                "name": "x",
                "timeseries_id": ts_1_id,
                "aggregation": "sum",
            }
            ret = client.put(
                f"{EXPRESSION_VARIABLES_URL}{var_1_id}",
                json=var_1_put,
                headers={"If-Match": var_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            var_1_etag = ret.headers["ETag"]
            assert ret_val["aggregation"] == "sum"
            assert ret_val["timeseries_id"] == ts_1_id
            assert ret_val["campaign_scope_id"] == cs_1_id
            assert ret_val["expression_id"] == expr_1_id

            # PUT wrong ID -> 404
            ret = client.put(
                f"{EXPRESSION_VARIABLES_URL}{DUMMY_ID}",
                json=var_1_put,
                headers={"If-Match": var_1_etag},
            )
            assert ret.status_code == 404

            # PUT with timeseries in wrong campaign scope
            var_1_bad_put = {
                "name": "x",
                "timeseries_id": ts_2_id,  # ts_2 in cs_2
                "aggregation": "avg",
            }
            ret = client.put(
                f"{EXPRESSION_VARIABLES_URL}{var_1_id}",
                json=var_1_bad_put,
                headers={"If-Match": var_1_etag},
            )
            assert ret.status_code == 422
            assert "_schema" in ret.json["errors"]["json"]

            # PUT non-existent timeseries_id -> 409
            ret = client.put(
                f"{EXPRESSION_VARIABLES_URL}{var_1_id}",
                json={"name": "x", "timeseries_id": DUMMY_ID, "aggregation": "avg"},
                headers={"If-Match": var_1_etag},
            )
            assert ret.status_code == 409

            # POST second variable (explicit aggregation)
            var_2 = {
                "campaign_scope_id": cs_2_id,
                "expression_id": expr_2_id,
                "name": "y",
                "timeseries_id": ts_4_id,
                "aggregation": "min",
            }
            ret = client.post(EXPRESSION_VARIABLES_URL, json=var_2)
            assert ret.status_code == 201
            ret_val = ret.json
            var_2_id = ret_val.pop("id")
            var_2_etag = ret.headers["ETag"]
            assert ret_val["aggregation"] == "min"

            # GET list (filtered by campaign_scope_id)
            ret = client.get(
                EXPRESSION_VARIABLES_URL,
                query_string={"campaign_scope_id": cs_1_id},
            )
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert ret.json[0]["id"] == var_1_id

            # GET list (filtered by expression_id)
            ret = client.get(
                EXPRESSION_VARIABLES_URL,
                query_string={"expression_id": expr_2_id},
            )
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert ret.json[0]["id"] == var_2_id

            # GET list (filtered by timeseries_id)
            ret = client.get(
                EXPRESSION_VARIABLES_URL,
                query_string={"timeseries_id": ts_4_id},
            )
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert ret.json[0]["id"] == var_2_id

            # GET by id wrong ID -> 404
            ret = client.get(f"{EXPRESSION_VARIABLES_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{EXPRESSION_VARIABLES_URL}{DUMMY_ID}",
                headers={"If-Match": "Dummy-ETag"},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{EXPRESSION_VARIABLES_URL}{var_1_id}",
                headers={"If-Match": var_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{EXPRESSION_VARIABLES_URL}{var_2_id}",
                headers={"If-Match": var_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(EXPRESSION_VARIABLES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{EXPRESSION_VARIABLES_URL}{var_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_expression_variables_as_user_api(
        self,
        app,
        users,
        campaign_scopes,
        timeseries,
        expressions,
        expression_variables,
    ):
        user_creds = users["Active"]["creds"]
        cs_1_id = campaign_scopes[0]
        ts_3_id = timeseries[2]  # in cs_1
        expr_1_id = expressions[0]
        var_1_id = expression_variables[0]
        var_2_id = expression_variables[1]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list - user only sees cs_1
            ret = client.get(EXPRESSION_VARIABLES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == var_1_id

            # POST -> 403 (no authorize_create defined)
            ret = client.post(
                EXPRESSION_VARIABLES_URL,
                json={
                    "campaign_scope_id": cs_1_id,
                    "expression_id": expr_1_id,
                    "name": "z",
                    "timeseries_id": ts_3_id,
                },
            )
            assert ret.status_code == 403

            # GET by id in scope
            ret = client.get(f"{EXPRESSION_VARIABLES_URL}{var_1_id}")
            assert ret.status_code == 200
            var_1_etag = ret.headers["ETag"]

            # PUT -> 403
            ret = client.put(
                f"{EXPRESSION_VARIABLES_URL}{var_1_id}",
                json={"name": "x", "timeseries_id": timeseries[0]},
                headers={"If-Match": var_1_etag},
            )
            assert ret.status_code == 403

            # GET by id not in scope -> 403
            ret = client.get(f"{EXPRESSION_VARIABLES_URL}{var_2_id}")
            assert ret.status_code == 403

            # DELETE -> 403
            ret = client.delete(
                f"{EXPRESSION_VARIABLES_URL}{var_1_id}",
                headers={"If-Match": var_1_etag},
            )
            assert ret.status_code == 403

    def test_expression_variables_as_anonym_api(self, app, expression_variables):
        var_1_id = expression_variables[0]

        client = app.test_client()

        # GET list
        ret = client.get(EXPRESSION_VARIABLES_URL)
        assert ret.status_code == 401

        # POST
        ret = client.post(
            EXPRESSION_VARIABLES_URL,
            json={
                "campaign_scope_id": 1,
                "expression_id": 1,
                "name": "x",
                "timeseries_id": 1,
            },
        )
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EXPRESSION_VARIABLES_URL}{var_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{EXPRESSION_VARIABLES_URL}{var_1_id}",
            json={"name": "x", "timeseries_id": 1},
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{EXPRESSION_VARIABLES_URL}{var_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401
