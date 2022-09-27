"""STCleanupByCampaigns routes tests"""
import pytest
from copy import deepcopy

from tests.common import AuthHeader


DUMMY_ID = "69"

ST_CLEANUPS_BY_CAMPAIGNS_URL = "/st_cleanups_by_campaigns/"


class TestST_CleanupByCampaignsApi:
    def test_st_cleanups_by_campaigns_api(self, app, users, campaigns):

        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(ST_CLEANUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            st_cbc_1 = {"campaign_id": campaign_1_id}
            ret = client.post(ST_CLEANUPS_BY_CAMPAIGNS_URL, json=st_cbc_1)
            assert ret.status_code == 201
            ret_val = ret.json
            st_cbc_1_id = ret_val.pop("id")
            st_cbc_1_etag = ret.headers["ETag"]
            st_cbc_1_expected = deepcopy(st_cbc_1)
            st_cbc_1_expected["is_enabled"] = True
            assert ret_val == st_cbc_1_expected

            # POST violating unique constraint
            ret = client.post(ST_CLEANUPS_BY_CAMPAIGNS_URL, json=st_cbc_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(ST_CLEANUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_1_id

            # GET by id
            ret = client.get(f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == st_cbc_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == st_cbc_1_expected

            # PUT
            st_cbc_1_expected["is_enabled"] = False
            ret = client.put(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}",
                json={"is_enabled": False},
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            st_cbc_1_etag = ret.headers["ETag"]
            assert ret_val == st_cbc_1_expected

            # PUT wrong ID -> 404
            ret = client.put(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{DUMMY_ID}",
                json={"is_enabled": False},
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 404

            # POST campaign 2
            st_cbc_2 = {"campaign_id": campaign_2_id}
            ret = client.post(ST_CLEANUPS_BY_CAMPAIGNS_URL, json=st_cbc_2)
            ret_val = ret.json
            st_cbc_2_id = ret_val.pop("id")
            st_cbc_2_etag = ret.headers["ETag"]

            # GET list
            ret = client.get(ST_CLEANUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                ST_CLEANUPS_BY_CAMPAIGNS_URL,
                query_string={"campaign_id": campaign_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_1_id

            # GET list (full), sort by campaign name
            ret = client.get(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}full",
                query_string={"sort": "+campaign_name"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == st_cbc_1_id
            assert ret_val[0]["campaign_id"] == campaign_1_id
            assert not ret_val[0]["is_enabled"]
            assert ret_val[1]["id"] == st_cbc_2_id
            assert ret_val[1]["campaign_id"] == campaign_2_id
            assert ret_val[1]["is_enabled"]

            # GET list (full), sort by campaign name and filter by state
            ret = client.get(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}full",
                query_string={"is_enabled": True, "sort": "+campaign_name"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_2_id
            assert ret_val[0]["campaign_id"] == campaign_2_id
            assert ret_val[0]["is_enabled"]

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{DUMMY_ID}",
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}",
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_2_id}",
                headers={"If-Match": st_cbc_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(ST_CLEANUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_st_cleanups_by_campaigns_as_user_api(
        self, app, users, campaigns, st_cleanups_by_campaigns
    ):

        user_creds = users["Active"]["creds"]
        campaign_1_id = campaigns[0]
        st_cbc_1_id = st_cleanups_by_campaigns[0]
        st_cbc_2_id = st_cleanups_by_campaigns[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(ST_CLEANUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            st_cbc_1 = ret_val[0]
            assert st_cbc_1["id"] == st_cbc_1_id

            # POST
            st_cbc_3 = {"campaign_id": campaign_1_id}
            ret = client.post(ST_CLEANUPS_BY_CAMPAIGNS_URL, json=st_cbc_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val["id"] == st_cbc_1_id
            st_cbc_1_etag = ret.headers["ETag"]
            ret = client.get(f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_2_id}")
            assert ret.status_code == 403

            # PUT
            ret = client.put(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}",
                json={"is_enabled": False},
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}",
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 403

            # GET list (full)
            ret = client.get(f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}full")
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_1_id

            # GET list (full), filter by state is_enabled
            ret = client.get(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}full",
                query_string={"is_enabled": False},
            )
            assert ret.status_code == 200
            assert len(ret.json) == 0

    def test_st_cleanups_by_campaigns_as_anonym_api(
        self, app, campaigns, st_cleanups_by_campaigns
    ):

        campaign_1_id = campaigns[0]
        st_cbc_1_id = st_cleanups_by_campaigns[0]

        client = app.test_client()

        # GET list
        ret = client.get(ST_CLEANUPS_BY_CAMPAIGNS_URL)
        assert ret.status_code == 401

        # POST
        st_cbc_3 = {"campaign_id": campaign_1_id}
        ret = client.post(ST_CLEANUPS_BY_CAMPAIGNS_URL, json=st_cbc_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}",
            json={"is_enabled": False},
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # GET list (full)
        ret = client.get(f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}full")
        assert ret.status_code == 401
