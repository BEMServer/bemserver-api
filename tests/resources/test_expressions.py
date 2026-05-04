"""Expressions tests"""

import pytest

from tests.common import AuthHeader

DUMMY_ID = 69

EXPRESSIONS_URL = "/expressions/"


class TestExpressionsApi:
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_expressions_api(self, app, users, campaign_scopes, timeseries):
        creds = users["Chuck"]["creds"]
        cs_1_id = campaign_scopes[0]
        cs_2_id = campaign_scopes[1]
        ts_1_id = timeseries[0]  # in cs_1
        ts_2_id = timeseries[1]  # in cs_2

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(EXPRESSIONS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            expr_1 = {
                "campaign_scope_id": cs_1_id,
                "expr": "x",
                "timeseries_id": ts_1_id,
            }
            ret = client.post(EXPRESSIONS_URL, json=expr_1)
            assert ret.status_code == 201
            ret_val = ret.json
            expr_1_id = ret_val.pop("id")
            expr_1_etag = ret.headers["ETag"]
            assert ret_val == expr_1

            # POST with timeseries in wrong campaign scope
            expr_bad_scope = {
                "campaign_scope_id": cs_1_id,
                "expr": "x",
                "timeseries_id": ts_2_id,
            }
            ret = client.post(EXPRESSIONS_URL, json=expr_bad_scope)
            assert ret.status_code == 422
            assert "_schema" in ret.json["errors"]["json"]

            # POST non-existent timeseries_id -> 409
            ret = client.post(
                EXPRESSIONS_URL,
                json={
                    "campaign_scope_id": cs_1_id,
                    "expr": "x",
                    "timeseries_id": DUMMY_ID,
                },
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(EXPRESSIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == expr_1_id

            # GET by id
            ret = client.get(f"{EXPRESSIONS_URL}{expr_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == expr_1_etag

            # PUT
            expr_1["expr"] = "2 * x"
            put_expr = expr_1.copy()
            del put_expr["campaign_scope_id"]
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json=put_expr,
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            expr_1_etag = ret.headers["ETag"]
            assert ret_val == expr_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{EXPRESSIONS_URL}{DUMMY_ID}",
                json=put_expr,
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 404

            # PUT with timeseries in wrong campaign scope
            put_expr_bad = put_expr.copy()
            put_expr_bad["timeseries_id"] = ts_2_id
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json=put_expr_bad,
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 422
            assert "_schema" in ret.json["errors"]["json"]

            # PUT non-existent timeseries_id -> 409
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json={**put_expr, "timeseries_id": DUMMY_ID},
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 409

            # POST second expression
            expr_2 = {
                "campaign_scope_id": cs_2_id,
                "expr": "y",
                "timeseries_id": ts_2_id,
            }
            ret = client.post(EXPRESSIONS_URL, json=expr_2)
            assert ret.status_code == 201
            ret_val = ret.json
            expr_2_id = ret_val.pop("id")
            expr_2_etag = ret.headers["ETag"]

            # GET list (filtered by campaign_scope_id)
            ret = client.get(
                EXPRESSIONS_URL,
                query_string={"campaign_scope_id": cs_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == expr_1_id

            # GET list (filtered by timeseries_id)
            ret = client.get(
                EXPRESSIONS_URL,
                query_string={"timeseries_id": ts_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == expr_2_id

            # GET by id wrong ID -> 404
            ret = client.get(f"{EXPRESSIONS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{EXPRESSIONS_URL}{DUMMY_ID}",
                headers={"If-Match": "Dummy-ETag"},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{EXPRESSIONS_URL}{expr_2_id}",
                headers={"If-Match": expr_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(EXPRESSIONS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{EXPRESSIONS_URL}{expr_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_expressions_as_user_api(
        self, app, users, campaign_scopes, timeseries, expressions
    ):
        user_creds = users["Active"]["creds"]
        ts_1_id = timeseries[0]  # in cs_1
        expr_1_id = expressions[0]
        expr_2_id = expressions[1]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list - user only sees cs_1
            ret = client.get(EXPRESSIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == expr_1_id

            # POST -> 403 (no authorize_create defined)
            ret = client.post(
                EXPRESSIONS_URL,
                json={
                    "campaign_scope_id": campaign_scopes[0],
                    "expr": "z",
                    "timeseries_id": ts_1_id,
                },
            )
            assert ret.status_code == 403

            # GET by id in scope
            ret = client.get(f"{EXPRESSIONS_URL}{expr_1_id}")
            assert ret.status_code == 200
            expr_1_etag = ret.headers["ETag"]

            # PUT -> 403
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json={"expr": "z", "timeseries_id": ts_1_id},
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 403

            # GET by id not in scope -> 403
            ret = client.get(f"{EXPRESSIONS_URL}{expr_2_id}")
            assert ret.status_code == 403

            # DELETE -> 403
            ret = client.delete(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 403

    def test_expressions_as_anonym_api(self, app, expressions):
        expr_1_id = expressions[0]

        client = app.test_client()

        # GET list
        ret = client.get(EXPRESSIONS_URL)
        assert ret.status_code == 401

        # POST
        ret = client.post(
            EXPRESSIONS_URL,
            json={"campaign_scope_id": 1, "expr": "x", "timeseries_id": 1},
        )
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EXPRESSIONS_URL}{expr_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{EXPRESSIONS_URL}{expr_1_id}",
            json={"expr": "x", "timeseries_id": 1},
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{EXPRESSIONS_URL}{expr_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401
