"""User groups by campaign scopes routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

USER_GROUPS_URL = "/user_groups/"
CAMPAIGN_SCOPES_URL = "/campaign_scopes/"
USER_GROUPS_BY_CAMPAIGN_SCOPES_URL = "/user_groups_by_campaign_scopes/"


class TestUsersByCampaignsApi:
    def test_user_groups_by_campaign_scopes_api(
        self, app, users, user_groups, campaign_scopes
    ):

        ug_1_id = user_groups[0]
        ug_2_id = user_groups[1]
        cs_1_id = campaign_scopes[0]
        cs_2_id = campaign_scopes[1]

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ugbc_1 = {"campaign_scope_id": cs_1_id, "user_group_id": ug_1_id}
            ret = client.post(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL, json=ugbc_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ugbc_1_id = ret_val.pop("id")
            ugbc_1_etag = ret.headers["ETag"]

            # POST violating unique constraint
            ret = client.post(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL, json=ugbc_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ugbc_1_id

            # GET by id
            ret = client.get(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{ugbc_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ugbc_1_etag

            # POST
            ugbc_2 = {"campaign_scope_id": cs_2_id, "user_group_id": ug_2_id}
            ret = client.post(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL, json=ugbc_2)
            assert ret.status_code == 201
            ret_val = ret.json
            ugbc_2_id = ret_val.pop("id")

            # GET list (filtered)
            ret = client.get(
                USER_GROUPS_BY_CAMPAIGN_SCOPES_URL,
                query_string={"user_group_id": ug_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ugbc_1_id
            assert ret_val[0]["user_group_id"] == ug_1_id
            assert ret_val[0]["campaign_scope_id"] == cs_1_id
            ret = client.get(
                USER_GROUPS_BY_CAMPAIGN_SCOPES_URL,
                query_string={"campaign_scope_id": cs_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ugbc_2_id
            assert ret_val[0]["user_group_id"] == ug_2_id
            assert ret_val[0]["campaign_scope_id"] == cs_2_id
            ret = client.get(
                USER_GROUPS_BY_CAMPAIGN_SCOPES_URL,
                query_string={"user_group_id": ug_1_id, "campaign_scope_id": cs_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # DELETE wrong ID -> 404
            ret = client.delete(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE
            ugbc_3 = {"campaign_scope_id": cs_1_id, "user_group_id": ug_2_id}
            ret = client.post(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL, json=ugbc_3)
            assert ret.status_code == 201
            ret_val = ret.json
            ugbc_3_id = ret_val.pop("id")
            ret = client.delete(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{ugbc_3_id}")
            assert ret.status_code == 204

            # DELETE user group cascade
            ret = client.get(f"{USER_GROUPS_URL}{ug_1_id}")
            ug_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{USER_GROUPS_URL}{ug_1_id}", headers={"If-Match": ug_1_etag}
            )
            assert ret.status_code == 204

            # DELETE campaign scope cascade
            ret = client.get(f"{CAMPAIGN_SCOPES_URL}{cs_2_id}")
            cs_2_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{CAMPAIGN_SCOPES_URL}{cs_2_id}", headers={"If-Match": cs_2_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{ugbc_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    def test_user_groups_by_campaign_scopes_as_user_api(
        self, app, users, user_groups, campaign_scopes, user_groups_by_campaign_scopes
    ):

        user_creds = users["Active"]["creds"]
        ug_1_id = user_groups[0]
        ug_2_id = user_groups[1]
        cs_1_id = campaign_scopes[0]
        cs_2_id = campaign_scopes[1]
        ugbc_1_id = user_groups_by_campaign_scopes[0]
        ugbc_2_id = user_groups_by_campaign_scopes[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ugbc_1 = ret_val[0]
            assert ugbc_1["id"] == ugbc_1_id

            # POST
            ugbc_3 = {"campaign_scope_id": cs_1_id, "user_group_id": ug_1_id}
            ret = client.post(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL, json=ugbc_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{ugbc_1_id}")
            assert ret.status_code == 200
            ret = client.get(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{ugbc_2_id}")
            assert ret.status_code == 403

            # GET list (filtered)
            ret = client.get(
                USER_GROUPS_BY_CAMPAIGN_SCOPES_URL,
                query_string={"user_group_id": ug_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ugbc_1_id
            assert ret_val[0]["user_group_id"] == ug_1_id
            assert ret_val[0]["campaign_scope_id"] == cs_1_id
            ret = client.get(
                USER_GROUPS_BY_CAMPAIGN_SCOPES_URL,
                query_string={"campaign_scope_id": cs_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(
                USER_GROUPS_BY_CAMPAIGN_SCOPES_URL,
                query_string={"user_group_id": ug_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # DELETE
            ret = client.delete(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{ugbc_1_id}")
            assert ret.status_code == 403

    def test_user_groups_by_campaign_scopes_as_anonym_api(
        self, app, users, user_groups, campaign_scopes, user_groups_by_campaign_scopes
    ):

        ug_1_id = user_groups[0]
        cs_1_id = campaign_scopes[0]
        ugbc_1_id = user_groups_by_campaign_scopes[0]

        client = app.test_client()

        # GET list
        ret = client.get(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL)
        assert ret.status_code == 401

        # POST
        ugbc_1 = {"campaign_scope_id": cs_1_id, "user_group_id": ug_1_id}
        ret = client.post(USER_GROUPS_BY_CAMPAIGN_SCOPES_URL, json=ugbc_1)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{ugbc_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{USER_GROUPS_BY_CAMPAIGN_SCOPES_URL}{ugbc_1_id}")
        assert ret.status_code == 401
