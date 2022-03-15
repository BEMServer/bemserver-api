"""User by user groups routes tests"""
from tests.common import AuthHeader


DUMMY_ID = "69"

USERS_URL = "/users/"
USER_GROUPS_URL = "/user_groups/"
USERS_BY_USER_GROUPS_URL = "/users_by_user_groups/"


class TestUsersByCampaignsApi:
    def test_users_by_user_groups_api(self, app, users, user_groups):

        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]
        ug_1_id = user_groups[0]
        ug_2_id = user_groups[1]

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(USERS_BY_USER_GROUPS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ubc_1 = {"user_group_id": ug_1_id, "user_id": user_1_id}
            ret = client.post(USERS_BY_USER_GROUPS_URL, json=ubc_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ubc_1_id = ret_val.pop("id")
            ubc_1_etag = ret.headers["ETag"]

            # POST violating unique constraint
            ret = client.post(USERS_BY_USER_GROUPS_URL, json=ubc_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(USERS_BY_USER_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ubc_1_id

            # GET by id
            ret = client.get(f"{USERS_BY_USER_GROUPS_URL}{ubc_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ubc_1_etag

            # POST
            ubc_2 = {"user_group_id": ug_2_id, "user_id": user_2_id}
            ret = client.post(USERS_BY_USER_GROUPS_URL, json=ubc_2)
            assert ret.status_code == 201
            ret_val = ret.json
            ubc_2_id = ret_val.pop("id")

            # GET list (filtered)
            ret = client.get(
                USERS_BY_USER_GROUPS_URL, query_string={"user_id": user_1_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ubc_1_id
            assert ret_val[0]["user_id"] == user_1_id
            assert ret_val[0]["user_group_id"] == ug_1_id
            ret = client.get(
                USERS_BY_USER_GROUPS_URL, query_string={"user_group_id": ug_2_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ubc_2_id
            assert ret_val[0]["user_id"] == user_2_id
            assert ret_val[0]["user_group_id"] == ug_2_id
            ret = client.get(
                USERS_BY_USER_GROUPS_URL,
                query_string={"user_id": user_1_id, "user_group_id": ug_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # DELETE wrong ID -> 404
            ret = client.delete(f"{USERS_BY_USER_GROUPS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE user violating fkey constraint
            ret = client.get(f"{USERS_URL}{user_1_id}")
            user_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{USERS_URL}{user_1_id}", headers={"If-Match": user_1_etag}
            )
            assert ret.status_code == 409

            # DELETE user_group violating fkey constraint
            ret = client.get(f"{USER_GROUPS_URL}{ug_1_id}")
            ug_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{USER_GROUPS_URL}{ug_1_id}", headers={"If-Match": ug_1_etag}
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(f"{USERS_BY_USER_GROUPS_URL}{ubc_1_id}")
            assert ret.status_code == 204
            ret = client.delete(f"{USERS_BY_USER_GROUPS_URL}{ubc_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(USERS_BY_USER_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{USERS_BY_USER_GROUPS_URL}{ubc_1_id}")
            assert ret.status_code == 404

    def test_users_by_user_groups_as_user_api(
        self, app, users, user_groups, users_by_user_groups
    ):

        user_creds = users["Active"]["creds"]
        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]
        ug_1_id = user_groups[0]
        ug_2_id = user_groups[1]
        ubc_1_id = users_by_user_groups[0]
        ubc_2_id = users_by_user_groups[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(USERS_BY_USER_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ubc_1 = ret_val[0]
            assert ubc_1["id"] == ubc_1_id

            # POST
            ubc_3 = {"user_group_id": ug_1_id, "user_id": user_1_id}
            ret = client.post(USERS_BY_USER_GROUPS_URL, json=ubc_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{USERS_BY_USER_GROUPS_URL}{ubc_1_id}")
            assert ret.status_code == 200
            ret = client.get(f"{USERS_BY_USER_GROUPS_URL}{ubc_2_id}")
            assert ret.status_code == 403

            # GET list (filtered)
            ret = client.get(
                USERS_BY_USER_GROUPS_URL, query_string={"user_id": user_1_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ubc_1_id
            assert ret_val[0]["user_id"] == user_1_id
            assert ret_val[0]["user_group_id"] == ug_1_id
            ret = client.get(
                USERS_BY_USER_GROUPS_URL, query_string={"user_group_id": ug_2_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(
                USERS_BY_USER_GROUPS_URL, query_string={"user_id": user_2_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # DELETE
            ret = client.delete(f"{USERS_BY_USER_GROUPS_URL}{ubc_1_id}")
            assert ret.status_code == 403

    def test_users_by_user_groups_as_anonym_api(
        self, app, users, user_groups, users_by_user_groups
    ):

        user_1_id = users["Active"]["id"]
        ug_1_id = user_groups[0]
        ubc_1_id = users_by_user_groups[0]

        client = app.test_client()

        # GET list
        ret = client.get(USERS_BY_USER_GROUPS_URL)
        assert ret.status_code == 401

        # POST
        ubc_1 = {"user_group_id": ug_1_id, "user_id": user_1_id}
        ret = client.post(USERS_BY_USER_GROUPS_URL, json=ubc_1)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{USERS_BY_USER_GROUPS_URL}{ubc_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{USERS_BY_USER_GROUPS_URL}{ubc_1_id}")
        assert ret.status_code == 401
