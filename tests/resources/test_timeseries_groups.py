"""Timeseries groups tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_GROUPS_URL = "/timeseries_groups/"


class TestTimeseriesGroupsApi:
    def test_timeseries_groups_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_GROUPS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tg_1 = {
                "name": "TS Group 1",
            }
            ret = client.post(TIMESERIES_GROUPS_URL, json=tg_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tg_1_id = ret_val.pop("id")
            tg_1_etag = ret.headers["ETag"]
            assert ret_val == tg_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_GROUPS_URL, json=tg_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tg_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tg_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tg_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tg_1

            # PUT
            tg_1["name"] = "Timeseries supergroup 1"
            ret = client.put(
                f"{TIMESERIES_GROUPS_URL}{tg_1_id}",
                json=tg_1,
                headers={"If-Match": tg_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tg_1_etag = ret.headers["ETag"]
            assert ret_val == tg_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_GROUPS_URL}{DUMMY_ID}",
                json=tg_1,
                headers={"If-Match": tg_1_etag},
            )
            assert ret.status_code == 404

            # POST TS 2
            tg_2 = {
                "name": "TS Group 2",
            }
            ret = client.post(TIMESERIES_GROUPS_URL, json=tg_2)
            ret_val = ret.json
            tg_2_id = ret_val.pop("id")
            tg_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tg_2["name"] = tg_1["name"]
            ret = client.put(
                f"{TIMESERIES_GROUPS_URL}{tg_2_id}",
                json=tg_2,
                headers={"If-Match": tg_2_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_GROUPS_URL}{tg_1_id}",
                headers={"If-Match": tg_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_GROUPS_URL}{tg_2_id}",
                headers={"If-Match": tg_2_etag},
            )

            # GET list
            ret = client.get(TIMESERIES_GROUPS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tg_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("timeseries_groups_by_users")
    def test_timeseries_groups_as_user_api(
        self, app, users, timeseries, timeseries_groups
    ):

        tg_1 = timeseries_groups[0]
        tg_1_id = timeseries[0]
        tg_2_id = timeseries[1]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["name"] == "TS Group 1"

            # POST
            tg_1 = {
                "name": "TS Group 1",
            }
            ret = client.post(TIMESERIES_GROUPS_URL, json=tg_1)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tg_1_id}")
            assert ret.status_code == 200
            ts_1_etag = ret.headers["ETag"]

            # GET by id, user not in group
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tg_2_id}")
            assert ret.status_code == 403

            # PUT
            tg_1["name"] = "Timeseries supergroup 1"
            ret = client.put(
                f"{TIMESERIES_GROUPS_URL}{tg_1_id}",
                json=tg_1,
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_GROUPS_URL}{tg_1_id}",
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

    def test_timeseries_groups_as_anonym_api(
        self, app, users, timeseries, timeseries_groups
    ):

        tg_1 = timeseries_groups[0]
        tg_1_id = timeseries[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_GROUPS_URL)
        assert ret.status_code == 401

        # POST
        tg_1 = {
            "name": "TS Group 1",
        }
        ret = client.post(TIMESERIES_GROUPS_URL, json=tg_1)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_GROUPS_URL}{tg_1_id}")
        assert ret.status_code == 401

        # PUT
        tg_1["name"] = "Timeseries supergroup 1"
        ret = client.put(
            f"{TIMESERIES_GROUPS_URL}{tg_1_id}",
            json=tg_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_GROUPS_URL}{tg_1_id}", headers={"If-Match": "Dummy-ETag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
