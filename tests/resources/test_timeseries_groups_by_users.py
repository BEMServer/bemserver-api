"""Timeseries group by user routes tests"""
from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIESS_URL = "/timeseries/"
TIMESERIES_GROUPS_URL = "/timeseries_groups/"
TIMESERIES_GROUPS_BY_USERS_URL = "/timeseries_groups_by_users/"


class TestTimeseriesGroupByUsersApi:
    def test_timeseries_groups_by_users_api(
        self, app, users, timeseries, timeseries_groups
    ):

        ts_1_id = timeseries[0]
        tsg_1_id = timeseries_groups[0]
        tsg_2_id = timeseries_groups[1]
        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_GROUPS_BY_USERS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tsgbu_1 = {"user_id": user_1_id, "timeseries_group_id": tsg_1_id}
            ret = client.post(TIMESERIES_GROUPS_BY_USERS_URL, json=tsgbu_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tsgbu_1_id = ret_val.pop("id")
            tsgbu_1_etag = ret.headers["ETag"]

            # POST violating unique constraint
            ret = client.post(TIMESERIES_GROUPS_BY_USERS_URL, json=tsgbu_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_GROUPS_BY_USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tsgbu_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tsgbu_1_etag

            # POST
            tsgbu_2 = {"user_id": user_2_id, "timeseries_group_id": tsg_2_id}
            ret = client.post(TIMESERIES_GROUPS_BY_USERS_URL, json=tsgbu_2)
            assert ret.status_code == 201
            ret_val = ret.json
            tsgbu_2_id = ret_val.pop("id")

            # GET list (filtered)
            ret = client.get(
                TIMESERIES_GROUPS_BY_USERS_URL,
                query_string={"timeseries_group_id": tsg_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tsgbu_1_id
            assert ret_val[0]["timeseries_group_id"] == tsg_1_id
            assert ret_val[0]["user_id"] == user_1_id
            ret = client.get(
                TIMESERIES_GROUPS_BY_USERS_URL,
                query_string={"user_id": user_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tsgbu_2_id
            assert ret_val[0]["timeseries_group_id"] == tsg_2_id
            assert ret_val[0]["user_id"] == user_2_id
            ret = client.get(
                TIMESERIES_GROUPS_BY_USERS_URL,
                query_string={
                    "timeseries_group_id": tsg_1_id,
                    "user_id": user_2_id,
                },
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET TS list filtered by user
            ret = client.get(TIMESERIESS_URL, query_string={"user_id": user_1_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{TIMESERIES_GROUPS_BY_USERS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE TS group violating fkey constraint
            ret = client.get(f"{TIMESERIES_GROUPS_URL}{tsg_1_id}")
            tsg_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{TIMESERIES_GROUPS_URL}{tsg_1_id}",
                headers={"If-Match": tsg_1_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_1_id}")
            assert ret.status_code == 204
            ret = client.delete(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_GROUPS_BY_USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_1_id}")
            assert ret.status_code == 404

    def test_timeseries_groups_by_users_as_user_api(
        self, app, users, timeseries_groups, timeseries_groups_by_users
    ):

        tsg_1_id = timeseries_groups[0]
        tsgbu_1_id = timeseries_groups_by_users[0]
        tsgbu_2_id = timeseries_groups_by_users[1]
        user_1_id = users["Active"]["id"]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_GROUPS_BY_USERS_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert ret.json[0]["id"] == tsgbu_1_id
            assert ret.json[0]["user_id"] == user_1_id
            assert ret.json[0]["timeseries_group_id"] == tsg_1_id

            # POST
            tsgbu = {"user_id": user_1_id, "timeseries_group_id": tsg_1_id}
            ret = client.post(TIMESERIES_GROUPS_BY_USERS_URL, json=tsgbu)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_2_id}")
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_1_id}")
            assert ret.status_code == 200

            # DELETE
            ret = client.delete(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_1_id}")
            assert ret.status_code == 403

    def test_timeseries_groups_by_users_as_anonym_api(
        self, app, users, timeseries_groups, timeseries_groups_by_users
    ):

        tsg_1_id = timeseries_groups[0]
        tsgbu_1_id = timeseries_groups_by_users[0]
        user_1_id = users["Active"]["id"]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_GROUPS_BY_USERS_URL)
        assert ret.status_code == 401

        # POST
        tsgbu = {"user_id": user_1_id, "timeseries_group_id": tsg_1_id}
        ret = client.post(TIMESERIES_GROUPS_BY_USERS_URL, json=tsgbu)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{TIMESERIES_GROUPS_BY_USERS_URL}{tsgbu_1_id}")
        assert ret.status_code == 401
