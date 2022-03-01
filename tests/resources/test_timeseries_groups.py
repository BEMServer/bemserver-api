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
            tsg_1 = {
                "name": "Timeseries group 1",
            }
            ret = client.post(TIMESERIES_GROUPS_URL, json=tsg_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tsg_1_id = ret_val.pop("id")
            tsg_1_etag = ret.headers["ETag"]
            assert ret_val == tsg_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_GROUPS_URL, json=tsg_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tsg_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tsg_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tsg_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tsg_1

            # PUT
            tsg_1["name"] = "Timeseries supergroup 1"
            ret = client.put(
                f"{TIMESERIES_GROUPS_URL}{tsg_1_id}",
                json=tsg_1,
                headers={"If-Match": tsg_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tsg_1_etag = ret.headers["ETag"]
            assert ret_val == tsg_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_GROUPS_URL}{DUMMY_ID}",
                json=tsg_1,
                headers={"If-Match": tsg_1_etag},
            )
            assert ret.status_code == 404

            # POST TSCG 2
            tsg_2 = {
                "name": "Timeseries group 2",
            }
            ret = client.post(TIMESERIES_GROUPS_URL, json=tsg_2)
            ret_val = ret.json
            tsg_2_id = ret_val.pop("id")
            tsg_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tsg_2["name"] = tsg_1["name"]
            ret = client.put(
                f"{TIMESERIES_GROUPS_URL}{tsg_2_id}",
                json=tsg_2,
                headers={"If-Match": tsg_2_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_GROUPS_URL}{tsg_1_id}",
                headers={"If-Match": tsg_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_GROUPS_URL}{tsg_2_id}",
                headers={"If-Match": tsg_2_etag},
            )

            # GET list
            ret = client.get(TIMESERIES_GROUPS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tsg_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("timeseries_groups_by_users")
    def test_timeseries_groups_as_user_api(self, app, users, timeseries_groups):

        tsg_1_id = timeseries_groups[0]
        tsg_2_id = timeseries_groups[1]

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
            tsg_1 = {
                "name": "Timeseries Group 1",
            }
            ret = client.post(TIMESERIES_GROUPS_URL, json=tsg_1)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tsg_1_id}")
            assert ret.status_code == 200
            ts_1_etag = ret.headers["ETag"]

            # GET by id, user not in group
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tsg_2_id}")
            assert ret.status_code == 403

            # PUT
            tsg_1["name"] = "Timeseries supergroup 1"
            ret = client.put(
                f"{TIMESERIES_GROUPS_URL}{tsg_1_id}",
                json=tsg_1,
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_GROUPS_URL}{tsg_1_id}",
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

    def test_timeseries_groups_as_anonym_api(self, app, users, timeseries_groups):

        tsg_1_id = timeseries_groups[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_GROUPS_URL)
        assert ret.status_code == 401

        # POST
        tsg_1 = {
            "name": "Timeseries group 1",
        }
        ret = client.post(TIMESERIES_GROUPS_URL, json=tsg_1)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_GROUPS_URL}{tsg_1_id}")
        assert ret.status_code == 401

        # PUT
        tsg_1["name"] = "Timeseries supergroup 1"
        ret = client.put(
            f"{TIMESERIES_GROUPS_URL}{tsg_1_id}",
            json=tsg_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_GROUPS_URL}{tsg_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
