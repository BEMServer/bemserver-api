"""User groups routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

USER_GROUPS_URL = "/user_groups/"


class TestUserGroupsApi:
    def test_user_groups_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(USER_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # POST
            ug_1 = {
                "name": "User group 1",
            }
            ret = client.post(USER_GROUPS_URL, json=ug_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ug_1_id = ret_val.pop("id")
            ug_1_etag = ret.headers["ETag"]
            assert ret_val == ug_1

            # POST violating unique constraint
            ret = client.post(USER_GROUPS_URL, json=ug_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(USER_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1

            # GET by id
            ret = client.get(f"{USER_GROUPS_URL}{ug_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ug_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == ug_1

            # PUT
            ug_1["name"] = "Super user group"
            ret = client.put(
                f"{USER_GROUPS_URL}{ug_1_id}",
                json=ug_1,
                headers={"If-Match": ug_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            ug_1_etag = ret.headers["ETag"]
            assert ret_val == ug_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{USER_GROUPS_URL}{DUMMY_ID}",
                json=ug_1,
                headers={"If-Match": ug_1_etag},
            )
            assert ret.status_code == 404

            # POST user 2
            ug_2 = {
                "name": "User group 2",
            }
            ret = client.post(USER_GROUPS_URL, json=ug_2)
            assert ret.status_code == 201
            ret_val = ret.json
            ug_2_id = ret_val.pop("id")
            ug_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            ug_2["name"] = ug_1["name"]
            ret = client.put(
                f"{USER_GROUPS_URL}{ug_2_id}",
                json=ug_2,
                headers={"If-Match": ug_2_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(USER_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{USER_GROUPS_URL}{DUMMY_ID}", headers={"If-Match": ug_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{USER_GROUPS_URL}{ug_1_id}", headers={"If-Match": ug_1_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(USER_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1

            # GET by id -> 404
            ret = client.get(f"{USER_GROUPS_URL}{ug_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    def test_user_groups_as_user_api(self, app, users, user_groups):

        creds = users["Active"]["creds"]
        ug_1_id = user_groups[0]
        ug_2_id = user_groups[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(USER_GROUPS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1

            # POST
            new_ug = {
                "name": "New user group",
            }
            ret = client.post(USER_GROUPS_URL, json=new_ug)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{USER_GROUPS_URL}{ug_1_id}")
            assert ret.status_code == 200
            ug_1 = ret.json
            ug_1_etag = ret.headers["ETag"]
            ret = client.get(f"{USER_GROUPS_URL}{ug_2_id}")
            assert ret.status_code == 403

            # PUT
            ug_1 = {
                "name": "Super user group 1",
            }
            ret = client.put(
                f"{USER_GROUPS_URL}{ug_1_id}",
                json=ug_1,
                headers={"If-Match": ug_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{USER_GROUPS_URL}{ug_1_id}", headers={"If-Match": ug_1_etag}
            )
            assert ret.status_code == 403

    def test_user_groups_as_anonym_api(self, app, users):

        ug_1_id = users["Active"]["id"]

        client = app.test_client()

        # GET list
        ret = client.get(USER_GROUPS_URL)
        assert ret.status_code == 401

        # POST
        new_ug = {
            "name": "New user group",
        }
        ret = client.post(USER_GROUPS_URL, json=new_ug)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{USER_GROUPS_URL}{ug_1_id}")
        assert ret.status_code == 401

        # PUT
        ug_1 = {
            "name": "Super user group",
        }
        ret = client.put(
            f"{USER_GROUPS_URL}{ug_1_id}", json=ug_1, headers={"If-Match": "Dummy-ETag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{USER_GROUPS_URL}{ug_1_id}", headers={"If-Match": "Dummy-ETag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
