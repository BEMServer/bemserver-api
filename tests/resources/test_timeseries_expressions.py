"""Timeseries expressions tests"""

import pytest

from tests.common import AuthHeader

DUMMY_ID = 69

TIMESERIES_EXPRESSIONS_URL = "/timeseries_expressions/"


class TestTimeseriesExpressionsApi:
    def test_timeseries_expressions_api(
        self, app, users, campaign_scopes, timeseries, expressions
    ):
        creds = users["Chuck"]["creds"]
        cs_1_id = campaign_scopes[0]
        cs_2_id = campaign_scopes[1]
        ts_1_id = timeseries[0]  # in cs_1
        ts_2_id = timeseries[1]  # in cs_2
        expr_1_id = expressions[0]  # in cs_1
        expr_2_id = expressions[1]  # in cs_2

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(TIMESERIES_EXPRESSIONS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ts_expr_1 = {
                "campaign_scope_id": cs_1_id,
                "expression_id": expr_1_id,
                "timeseries_id": ts_1_id,
                "src_data_state_id": 1,
                "dest_data_state_id": 2,
                "bucket_width_value": 1,
                "bucket_width_unit": "hour",
            }
            ret = client.post(TIMESERIES_EXPRESSIONS_URL, json=ts_expr_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ts_expr_1_id = ret_val.pop("id")
            ts_expr_1_etag = ret.headers["ETag"]
            assert ret_val.pop("timezone") == "UTC"
            assert ret_val == ts_expr_1

            # GET list
            ret = client.get(TIMESERIES_EXPRESSIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_expr_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ts_expr_1_etag
            ret_val = ret.json
            assert ret_val["id"] == ts_expr_1_id

            # PUT
            ts_expr_1["bucket_width_value"] = 2
            put_ts_expr = ts_expr_1.copy()
            del put_ts_expr["campaign_scope_id"]
            del put_ts_expr["expression_id"]
            ret = client.put(
                f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}",
                json=put_ts_expr,
                headers={"If-Match": ts_expr_1_etag},
            )
            assert ret.status_code == 200
            ts_expr_1_etag = ret.headers["ETag"]
            ret_val = ret.json
            assert ret_val["bucket_width_value"] == 2

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_EXPRESSIONS_URL}{DUMMY_ID}",
                json=put_ts_expr,
                headers={"If-Match": ts_expr_1_etag},
            )
            assert ret.status_code == 404

            # POST second timeseries expression
            ts_expr_2 = {
                "campaign_scope_id": cs_2_id,
                "expression_id": expr_2_id,
                "timeseries_id": ts_2_id,
                "src_data_state_id": 1,
                "dest_data_state_id": 2,
                "bucket_width_value": 1,
                "bucket_width_unit": "day",
            }
            ret = client.post(TIMESERIES_EXPRESSIONS_URL, json=ts_expr_2)
            assert ret.status_code == 201
            ret_val = ret.json
            ts_expr_2_id = ret_val.pop("id")
            ts_expr_2_etag = ret.headers["ETag"]

            # POST with TS not in CS
            ts_expr_3 = {
                "campaign_scope_id": cs_1_id,
                "expression_id": expr_1_id,
                "timeseries_id": ts_2_id,
                "src_data_state_id": 1,
                "dest_data_state_id": 2,
                "bucket_width_value": 1,
                "bucket_width_unit": "hour",
            }
            ret = client.post(TIMESERIES_EXPRESSIONS_URL, json=ts_expr_3)
            assert ret.status_code == 422

            # POST with expression not in CS
            ts_expr_3 = {
                "campaign_scope_id": cs_1_id,
                "expression_id": expr_2_id,
                "timeseries_id": ts_1_id,
                "src_data_state_id": 1,
                "dest_data_state_id": 2,
                "bucket_width_value": 1,
                "bucket_width_unit": "hour",
            }
            ret = client.post(TIMESERIES_EXPRESSIONS_URL, json=ts_expr_3)
            assert ret.status_code == 422

            # POST with unknown TS
            ts_expr_4 = {
                "campaign_scope_id": cs_1_id,
                "expression_id": expr_1_id,
                "timeseries_id": DUMMY_ID,
                "src_data_state_id": 1,
                "dest_data_state_id": 2,
                "bucket_width_value": 1,
                "bucket_width_unit": "hour",
            }
            ret = client.post(TIMESERIES_EXPRESSIONS_URL, json=ts_expr_4)
            assert ret.status_code == 409

            # POST with unknown expression
            ts_expr_4 = {
                "campaign_scope_id": cs_1_id,
                "expression_id": DUMMY_ID,
                "timeseries_id": ts_1_id,
                "src_data_state_id": 1,
                "dest_data_state_id": 2,
                "bucket_width_value": 1,
                "bucket_width_unit": "hour",
            }
            ret = client.post(TIMESERIES_EXPRESSIONS_URL, json=ts_expr_4)
            assert ret.status_code == 409

            # GET list (filtered by campaign_scope_id)
            ret = client.get(
                TIMESERIES_EXPRESSIONS_URL,
                query_string={"campaign_scope_id": cs_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_expr_1_id

            # GET by id wrong ID -> 404
            ret = client.get(f"{TIMESERIES_EXPRESSIONS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{TIMESERIES_EXPRESSIONS_URL}{DUMMY_ID}",
                headers={"If-Match": "Dummy-ETag"},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}",
                headers={"If-Match": ts_expr_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_2_id}",
                headers={"If-Match": ts_expr_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_EXPRESSIONS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_timeseries_expressions_as_user_api(
        self, app, users, campaign_scopes, timeseries, expressions, ts_expressions
    ):
        user_creds = users["Active"]["creds"]
        cs_1_id = campaign_scopes[0]
        ts_1_id = timeseries[0]  # in cs_1
        expr_1_id = expressions[0]  # in cs_1
        ts_expr_1_id = ts_expressions[0]  # in cs_1
        ts_expr_2_id = ts_expressions[1]  # in cs_2

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list - user only sees cs_1
            ret = client.get(TIMESERIES_EXPRESSIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_expr_1_id

            # GET by id in scope
            ret = client.get(f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}")
            assert ret.status_code == 200
            ts_expr_1_etag = ret.headers["ETag"]

            # POST -> 403 (no authorize_create defined)
            ret = client.post(
                TIMESERIES_EXPRESSIONS_URL,
                json={
                    "campaign_scope_id": cs_1_id,
                    "expression_id": expr_1_id,
                    "timeseries_id": ts_1_id,
                    "src_data_state_id": 1,
                    "dest_data_state_id": 2,
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                },
            )
            assert ret.status_code == 403

            # PUT -> 403
            ret = client.put(
                f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}",
                json={
                    "timeseries_id": ts_1_id,
                    "src_data_state_id": 1,
                    "dest_data_state_id": 2,
                    "bucket_width_value": 2,
                    "bucket_width_unit": "hour",
                },
                headers={"If-Match": ts_expr_1_etag},
            )
            assert ret.status_code == 403

            # GET by id not in scope -> 403
            ret = client.get(f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_2_id}")
            assert ret.status_code == 403

            # DELETE -> 403
            ret = client.delete(
                f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}",
                headers={"If-Match": ts_expr_1_etag},
            )
            assert ret.status_code == 403

    def test_timeseries_expressions_as_anonym_api(self, app, ts_expressions):
        ts_expr_1_id = ts_expressions[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_EXPRESSIONS_URL)
        assert ret.status_code == 401

        # POST
        ret = client.post(TIMESERIES_EXPRESSIONS_URL, json={})
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}",
            json={"bucket_width_value": 2},
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_EXPRESSIONS_URL}{ts_expr_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401
