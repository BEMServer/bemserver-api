"""Timeseries tests"""
import contextlib

import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_URL = "/timeseries/"
CAMPAIGNS_URL = "/campaigns/"


class TestTimeseriesApi:
    def test_timeseries_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            timeseries_1 = {
                "name": "Timeseries 1",
                "description": "Timeseries example 1",
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == 201
            ret_val = ret.json
            timeseries_1_id = ret_val.pop("id")
            timeseries_1_etag = ret.headers["ETag"]
            assert ret_val == timeseries_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == timeseries_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == timeseries_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == timeseries_1

            # PUT
            del timeseries_1["description"]
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                json=timeseries_1,
                headers={"If-Match": timeseries_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            timeseries_1_etag = ret.headers["ETag"]
            assert ret_val == timeseries_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_URL}{DUMMY_ID}",
                json=timeseries_1,
                headers={"If-Match": timeseries_1_etag},
            )
            assert ret.status_code == 404

            # POST TS 2
            timeseries_2 = {
                "name": "Timeseries 2",
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_2)
            ret_val = ret.json
            timeseries_2_id = ret_val.pop("id")
            timeseries_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            timeseries_2["name"] = timeseries_1["name"]
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_2_id}",
                json=timeseries_2,
                headers={"If-Match": timeseries_2_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                headers={"If-Match": timeseries_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_URL}{timeseries_2_id}",
                headers={"If-Match": timeseries_2_etag},
            )

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == 404

    @pytest.mark.parametrize("user", ("user", "anonym"))
    def test_timeseries_as_user_or_anonym_api(self, app, user, users, timeseries):

        timeseries_1_id = timeseries[0]

        if user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
            status_code = 403
        else:
            auth_context = contextlib.nullcontext()
            status_code = 401

        client = app.test_client()

        with auth_context:

            # GET list
            ret = client.get(TIMESERIES_URL)
            if user == "user":
                assert ret.status_code == 200
                assert not ret.json
            else:
                assert ret.status_code == status_code

            # POST
            timeseries_1 = {
                "name": "Timeseries 1",
                "description": "Timeseries example 1",
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == status_code

            # GET by id
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == status_code

            # PUT
            del timeseries_1["description"]
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                json=timeseries_1,
                headers={"If-Match": "Dummy-ETag"},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == status_code

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_URL}{timeseries_1_id}", headers={"If-Match": "Dummy-ETag"}
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == status_code
