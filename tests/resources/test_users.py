"""Users routes tests"""
DUMMY_ID = "69"

USERS_URL = "/users/"


class TestUsersApi:

    def test_users_api(self, app):

        client = app.test_client()

        # GET list
        ret = client.get(USERS_URL)
        assert ret.status_code == 200
        assert ret.json == []

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

        # GET list
        ret = client.get(USERS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == user_1_id

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
            headers={"If-Match": user_1_etag}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        ret_val.pop("id")
        user_1_etag = ret.headers["ETag"]
        assert ret_val == user_1_expected_get

        # PUT wrong ID -> 404
        ret = client.put(
            f"{USERS_URL}{DUMMY_ID}",
            json=user_1,
            headers={"If-Match": user_1_etag}
        )
        assert ret.status_code == 404

        # Set admin
        ret = client.put(
            f"{USERS_URL}{user_1_id}/set_admin",
            json={"value": True},
            headers={"If-Match": user_1_etag}
        )
        assert ret.status_code == 204
        user_1_etag = ret.headers["ETag"]

        # Set admin wrong ID -> 404
        ret = client.put(
            f"{USERS_URL}{DUMMY_ID}/set_admin",
            json={"value": True},
            headers={"If-Match": user_1_etag}
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

        # Set inactive
        ret = client.put(
            f"{USERS_URL}{user_2_id}/set_active",
            json={"value": False},
            headers={"If-Match": user_2_etag}
        )
        assert ret.status_code == 204
        user_2_etag = ret.headers["ETag"]

        # Set inactive wrong ID -> 404
        ret = client.put(
            f"{USERS_URL}{DUMMY_ID}/set_active",
            json={"value": False},
            headers={"If-Match": user_2_etag}
        )
        assert ret.status_code == 404

        # GET list
        ret = client.get(USERS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 2

        # GET list (filtered)
        ret = client.get(USERS_URL, query_string={"is_admin": True})
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == user_1_id
        ret = client.get(USERS_URL, query_string={"is_active": False})
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == user_2_id

        # DELETE wrong ID -> 404
        ret = client.delete(
            f"{USERS_URL}{DUMMY_ID}",
            headers={"If-Match": user_1_etag}
        )
        assert ret.status_code == 404

        # DELETE
        ret = client.delete(
            f"{USERS_URL}{user_1_id}",
            headers={"If-Match": user_1_etag}
        )
        assert ret.status_code == 204

        # GET list
        ret = client.get(USERS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1

        # GET by id -> 404
        ret = client.get(f"{USERS_URL}{user_1_id}")
        assert ret.status_code == 404
