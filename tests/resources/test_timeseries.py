"""Timeseries tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_URL = "/timeseries/"


class TestTimeseriesApi:
    def test_timeseries_api(self, app, users, timeseries_groups):

        creds = users["Chuck"]["creds"]
        tg_1 = timeseries_groups[0]
        tg_2 = timeseries_groups[1]

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
                "group_id": tg_1,
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
                "group_id": tg_2,
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

    @pytest.mark.usefixtures("timeseries_groups_by_users")
    def test_timeseries_as_user_api(self, app, users, timeseries, timeseries_groups):

        tg_1 = timeseries_groups[0]
        timeseries_1_id = timeseries[0]
        timeseries_2_id = timeseries[1]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["group_id"] == tg_1

            # POST
            timeseries_1 = {
                "name": "Timeseries 1",
                "description": "Timeseries example 1",
                "group_id": tg_1,
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == 200
            ts_1_etag = ret.headers["ETag"]

            # GET by id, user not in group
            ret = client.get(f"{TIMESERIES_URL}{timeseries_2_id}")
            assert ret.status_code == 403

            # PUT
            del timeseries_1["description"]
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                json=timeseries_1,
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

    def test_timeseries_as_anonym_api(self, app, users, timeseries, timeseries_groups):

        tg_1 = timeseries_groups[0]
        timeseries_1_id = timeseries[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_URL)
        assert ret.status_code == 401

        # POST
        timeseries_1 = {
            "name": "Timeseries 1",
            "description": "Timeseries example 1",
            "group_id": tg_1,
        }
        ret = client.post(TIMESERIES_URL, json=timeseries_1)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
        assert ret.status_code == 401

        # PUT
        del timeseries_1["description"]
        ret = client.put(
            f"{TIMESERIES_URL}{timeseries_1_id}",
            json=timeseries_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_URL}{timeseries_1_id}", headers={"If-Match": "Dummy-ETag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
