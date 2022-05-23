"""Users routes tests"""
from tests.common import AuthHeader


DUMMY_ID = "69"

USERS_URL = "/users/"


class TestUsersApi:
    def test_users_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            nb_init_users = len(ret_val)
            init_admin_users_ids = {u["id"] for u in ret_val if u["is_admin"]}
            init_inactive_users_ids = {u["id"] for u in ret_val if not u["is_active"]}

            # POST
            user_1 = {
                "name": "User 1",
                "email": "user_1@test.com",
                "password": "p@ss",
            }
            user_1_expected_get = {
                "name": "User 1",
                "email": "user_1@test.com",
                "is_admin": False,
                "is_active": True,
            }
            ret = client.post(USERS_URL, json=user_1)
            assert ret.status_code == 201
            ret_val = ret.json
            user_1_id = ret_val.pop("id")
            user_1_etag = ret.headers["ETag"]
            assert ret_val == user_1_expected_get

            # POST violating unique constraint
            ret = client.post(USERS_URL, json=user_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_init_users + 1

            # GET by id
            ret = client.get(f"{USERS_URL}{user_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == user_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == user_1_expected_get

            # PUT
            user_1["email"] = "user_1-spam@test.com"
            user_1_expected_get["email"] = "user_1-spam@test.com"
            ret = client.put(
                f"{USERS_URL}{user_1_id}",
                json=user_1,
                headers={"If-Match": user_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            user_1_etag = ret.headers["ETag"]
            assert ret_val == user_1_expected_get

            # PUT wrong ID -> 404
            ret = client.put(
                f"{USERS_URL}{DUMMY_ID}", json=user_1, headers={"If-Match": user_1_etag}
            )
            assert ret.status_code == 404

            # Set admin
            ret = client.put(
                f"{USERS_URL}{user_1_id}/set_admin",
                json={"value": True},
                headers={"If-Match": user_1_etag},
            )
            assert ret.status_code == 204
            user_1_etag = ret.headers["ETag"]

            # Set admin wrong ID -> 404
            ret = client.put(
                f"{USERS_URL}{DUMMY_ID}/set_admin",
                json={"value": True},
                headers={"If-Match": user_1_etag},
            )
            assert ret.status_code == 404

            # POST user 2
            user_2 = {
                "name": "User 2",
                "email": "user_2@test.com",
                "password": "pa55",
            }
            ret = client.post(USERS_URL, json=user_2)
            assert ret.status_code == 201
            ret_val = ret.json
            user_2_id = ret_val.pop("id")
            user_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            user_2["email"] = user_1["email"]
            ret = client.put(
                f"{USERS_URL}{user_2_id}",
                json=user_2,
                headers={"If-Match": user_2_etag},
            )
            assert ret.status_code == 409

            # Set inactive
            ret = client.put(
                f"{USERS_URL}{user_2_id}/set_active",
                json={"value": False},
                headers={"If-Match": user_2_etag},
            )
            assert ret.status_code == 204
            user_2_etag = ret.headers["ETag"]

            # Set inactive wrong ID -> 404
            ret = client.put(
                f"{USERS_URL}{DUMMY_ID}/set_active",
                json={"value": False},
                headers={"If-Match": user_2_etag},
            )
            assert ret.status_code == 404

            # GET list
            ret = client.get(USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_init_users + 2

            # GET list (filtered)
            ret = client.get(USERS_URL, query_string={"is_admin": True})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == len(init_admin_users_ids) + 1
            assert {u["id"] for u in ret_val} == init_admin_users_ids | {user_1_id}
            ret = client.get(USERS_URL, query_string={"is_active": False})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == len(init_inactive_users_ids) + 1
            assert {u["id"] for u in ret_val} == init_inactive_users_ids | {user_2_id}

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{USERS_URL}{DUMMY_ID}", headers={"If-Match": user_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{USERS_URL}{user_1_id}", headers={"If-Match": user_1_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_init_users + 1

            # GET by id -> 404
            ret = client.get(f"{USERS_URL}{user_1_id}")
            assert ret.status_code == 404

    def test_users_as_user_api(self, app, users):

        creds = users["Active"]["creds"]
        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1

            # POST
            new_user = {
                "name": "New user",
                "email": "new_user@test.com",
                "password": "p@ss",
            }
            ret = client.post(USERS_URL, json=new_user)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{USERS_URL}{user_1_id}")
            assert ret.status_code == 200
            user_1 = ret.json
            user_1_etag = ret.headers["ETag"]
            ret = client.get(f"{USERS_URL}{user_2_id}")
            assert ret.status_code == 403

            # PUT
            user_1 = {
                "name": "Superactive",
                "password": "@ctive",
                "email": "active@test.com",
            }
            ret = client.put(
                f"{USERS_URL}{user_1_id}",
                json=user_1,
                headers={"If-Match": user_1_etag},
            )
            assert ret.status_code == 200
            user_1_etag = ret.headers["ETag"]
            ret = client.put(
                f"{USERS_URL}{user_2_id}",
                json=new_user,
                headers={"If-Match": user_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

            # Set admin
            ret = client.put(
                f"{USERS_URL}{user_1_id}/set_admin",
                json={"value": True},
                headers={"If-Match": user_1_etag},
            )
            assert ret.status_code == 403

            # Set inactive
            ret = client.put(
                f"{USERS_URL}{user_1_id}/set_active",
                json={"value": False},
                headers={"If-Match": user_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{USERS_URL}{user_1_id}", headers={"If-Match": user_1_etag}
            )
            assert ret.status_code == 403

    def test_users_as_anonym_api(self, app, users):

        user_1_id = users["Active"]["id"]

        client = app.test_client()

        # GET list
        ret = client.get(USERS_URL)
        assert ret.status_code == 401

        # POST
        new_user = {
            "name": "New user",
            "email": "new_user@test.com",
            "password": "p@ss",
        }
        ret = client.post(USERS_URL, json=new_user)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{USERS_URL}{user_1_id}")
        assert ret.status_code == 401

        # PUT
        user_1 = {
            "name": "Superactive",
            "password": "@ctive",
            "email": "active@test.com",
        }
        ret = client.put(
            f"{USERS_URL}{user_1_id}", json=user_1, headers={"If-Match": "Dummy-ETag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # Set admin
        ret = client.put(
            f"{USERS_URL}{user_1_id}/set_admin",
            json={"value": True},
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # Set inactive
        ret = client.put(
            f"{USERS_URL}{user_1_id}/set_active",
            json={"value": False},
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{USERS_URL}{user_1_id}", headers={"If-Match": "Dummy-ETag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
