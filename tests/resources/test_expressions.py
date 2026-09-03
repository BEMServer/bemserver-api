"""Expressions tests"""

import datetime as dt

import pytest

from tests.common import AuthHeader

DUMMY_ID = 69

EXPRESSIONS_URL = "/expressions/"


class TestExpressionsApi:
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
            var_1 = {
                "name": "a",
                "timeseries_id": ts_1_id,
            }
            expr_1 = {
                "campaign_scope_id": cs_1_id,
                "name": "a",
                "expr": "a",
                "variables": [var_1],
            }
            ret = client.post(EXPRESSIONS_URL, json=expr_1)
            assert ret.status_code == 201
            ret_val = ret.json
            expr_1_id = ret_val.pop("id")
            expr_1_etag = ret.headers["ETag"]
            assert ret_val["variables"][0].pop("aggregation") == "avg"
            assert ret_val == expr_1

            # GET list
            ret = client.get(EXPRESSIONS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0].pop("id") == expr_1_id
            assert ret_val[0]["variables"][0].pop("aggregation") == "avg"
            assert ret_val[0] == expr_1

            # GET by id
            ret = client.get(f"{EXPRESSIONS_URL}{expr_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == expr_1_etag
            ret_val = ret.json
            assert ret_val.pop("id") == expr_1_id
            assert ret_val["variables"][0].pop("aggregation") == "avg"
            assert ret_val == expr_1

            # PUT
            expr_1["name"] = "2 times a"
            expr_1["expr"] = "2*a"
            put_expr = expr_1.copy()
            del put_expr["campaign_scope_id"]
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json=put_expr,
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 200
            expr_1_etag = ret.headers["ETag"]
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val["variables"][0].pop("aggregation") == "avg"
            assert ret_val == expr_1

            # PUT invalid (variable name doesn't match expression)
            put_expr = expr_1.copy()
            put_expr["name"] = "2 times x"
            put_expr["expr"] = "2*x"
            del put_expr["campaign_scope_id"]
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json=put_expr,
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 422

            # PUT wrong ID -> 404
            ret = client.put(
                f"{EXPRESSIONS_URL}{DUMMY_ID}",
                json=put_expr,
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 404

            # POST second expression
            var_2 = {
                "name": "b",
                "timeseries_id": ts_2_id,
            }
            expr_2 = {
                "campaign_scope_id": cs_2_id,
                "name": "b",
                "expr": "b",
                "variables": [var_2],
            }
            ret = client.post(EXPRESSIONS_URL, json=expr_2)
            assert ret.status_code == 201
            ret_val = ret.json
            expr_2_id = ret_val.pop("id")
            expr_2_etag = ret.headers["ETag"]

            # POST invalid expression (variable name doesn't match expression)
            var_3 = {
                "name": "x",
                "timeseries_id": ts_1_id,
            }
            expr_3 = {
                "campaign_scope_id": cs_1_id,
                "name": "c",
                "expr": "c",
                "variables": [var_3],
            }
            ret = client.post(EXPRESSIONS_URL, json=expr_3)
            assert ret.status_code == 422

            # POST with TS not in CS
            var_1 = {
                "name": "a",
                "timeseries_id": ts_2_id,
            }
            expr_1 = {
                "campaign_scope_id": cs_1_id,
                "name": "a",
                "expr": "a",
                "variables": [var_1],
            }
            ret = client.post(EXPRESSIONS_URL, json=expr_1)
            assert ret.status_code == 422

            # PUT with TS not in CS
            put_expr = expr_1.copy()
            del put_expr["campaign_scope_id"]
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json=put_expr,
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 422

            # POST with unknown TS
            var_1 = {
                "name": "a",
                "timeseries_id": DUMMY_ID,
            }
            expr_1 = {
                "campaign_scope_id": cs_1_id,
                "name": "a",
                "expr": "a",
                "variables": [var_1],
            }
            ret = client.post(EXPRESSIONS_URL, json=expr_1)
            assert ret.status_code == 409

            # PUT with unknown TS
            put_expr = expr_1.copy()
            del put_expr["campaign_scope_id"]
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json=put_expr,
                headers={"If-Match": expr_1_etag},
            )
            assert ret.status_code == 409

            # GET list (filtered by campaign_scope_id)
            ret = client.get(
                EXPRESSIONS_URL,
                query_string={"campaign_scope_id": cs_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == expr_1_id

            # GET list with pagination
            ret = client.get(
                EXPRESSIONS_URL,
                query_string={"page_size": 1, "page": 2, "sort": "id"},
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
        cs_1_id = campaign_scopes[0]
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

            var_1 = {
                "name": "a",
                "timeseries_id": ts_1_id,
            }
            expr_1 = {
                "campaign_scope_id": cs_1_id,
                "name": "a",
                "expr": "a",
                "variables": [var_1],
            }

            # POST -> 403 (no authorize_create defined)
            ret = client.post(
                EXPRESSIONS_URL,
                json=expr_1,
            )
            assert ret.status_code == 403

            # GET by id in scope
            ret = client.get(f"{EXPRESSIONS_URL}{expr_1_id}")
            assert ret.status_code == 200
            expr_1_etag = ret.headers["ETag"]

            # PUT -> 403
            ret = client.put(
                f"{EXPRESSIONS_URL}{expr_1_id}",
                json={"name": "2 times a", "expr": "2*a", "variables": [var_1]},
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

    def test_expressions_as_anonym_api(
        self, app, campaign_scopes, timeseries, expressions
    ):
        cs_1_id = campaign_scopes[0]
        ts_1_id = timeseries[0]  # in cs_1
        expr_1_id = expressions[0]

        client = app.test_client()

        # GET list
        ret = client.get(EXPRESSIONS_URL)
        assert ret.status_code == 401

        var_1 = {
            "name": "a",
            "timeseries_id": ts_1_id,
        }
        expr_1 = {
            "campaign_scope_id": cs_1_id,
            "name": "a",
            "expr": "a",
            "variables": [var_1],
        }

        # POST
        ret = client.post(
            EXPRESSIONS_URL,
            json=expr_1,
        )
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EXPRESSIONS_URL}{expr_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{EXPRESSIONS_URL}{expr_1_id}",
            json={"name": "2 times a", "expr": "2*a", "variables": [var_1]},
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{EXPRESSIONS_URL}{expr_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401

    def test_expressions_evaluate(
        self, app, users, campaign_scopes, timeseries, timeseries_data
    ):
        admin_creds = users["Chuck"]["creds"]
        user_creds = users["Active"]["creds"]
        ts_1_id = timeseries[0]  # in cs_1

        start_dt = dt.datetime(2020, 1, 1, tzinfo=dt.UTC)
        end_dt = dt.datetime(2020, 1, 2, tzinfo=dt.UTC)

        client = app.test_client()

        var_1 = {
            "name": "a",
            "timeseries_id": ts_1_id,
        }
        expr_1 = {
            "name": "a",
            "expr": "a",
            "variables": [var_1],
        }
        ds_id = 1

        with AuthHeader(admin_creds):
            ret = client.post(
                f"{EXPRESSIONS_URL}evaluate",
                json=expr_1,
                query_string={
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                    "data_state": ds_id,
                    "timezone": "UTC",
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                },
            )
            assert ret.status_code == 200
            assert ret.json == {
                "2020-01-01T00:00:00+00:00": 0.0,
                "2020-01-01T01:00:00+00:00": 1.0,
                "2020-01-01T02:00:00+00:00": 2.0,
                "2020-01-01T03:00:00+00:00": 3.0,
            }

        with AuthHeader(user_creds):
            ret = client.post(
                f"{EXPRESSIONS_URL}evaluate",
                json=expr_1,
                query_string={
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                    "data_state": ds_id,
                    "timezone": "UTC",
                    "bucket_width_value": 1,
                    "bucket_width_unit": "hour",
                },
            )
            assert ret.status_code == 403

    def test_expressions_evaluate_by_id(
        self, app, users, campaign_scopes, timeseries, timeseries_data
    ):
        admin_creds = users["Chuck"]["creds"]
        user_creds = users["Active"]["creds"]
        cs_1_id = campaign_scopes[0]
        ts_1_id = timeseries[0]  # in cs_1

        start_dt = dt.datetime(2020, 1, 1, tzinfo=dt.UTC)
        end_dt = dt.datetime(2020, 1, 2, tzinfo=dt.UTC)

        client = app.test_client()

        var_1 = {
            "name": "a",
            "timeseries_id": ts_1_id,
        }
        expr_1 = {
            "campaign_scope_id": cs_1_id,
            "name": "a",
            "expr": "a",
            "variables": [var_1],
        }
        ds_id = 1
        query_string = {
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "data_state": ds_id,
            "timezone": "UTC",
            "bucket_width_value": 1,
            "bucket_width_unit": "hour",
        }

        with AuthHeader(admin_creds):
            ret = client.post(EXPRESSIONS_URL, json=expr_1)
            assert ret.status_code == 201
            expr_1_id = ret.json["id"]

            ret = client.get(
                f"{EXPRESSIONS_URL}{expr_1_id}/evaluate",
                query_string=query_string,
            )
            assert ret.status_code == 200
            assert ret.json == {
                "2020-01-01T00:00:00+00:00": 0.0,
                "2020-01-01T01:00:00+00:00": 1.0,
                "2020-01-01T02:00:00+00:00": 2.0,
                "2020-01-01T03:00:00+00:00": 3.0,
            }

            # Evaluate by ID, wrong ID -> 404
            ret = client.get(
                f"{EXPRESSIONS_URL}{DUMMY_ID}/evaluate",
                query_string=query_string,
            )
            assert ret.status_code == 404

        with AuthHeader(user_creds):
            ret = client.get(
                f"{EXPRESSIONS_URL}{expr_1_id}/evaluate",
                query_string=query_string,
            )
            assert ret.status_code == 403
