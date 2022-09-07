"""STCleanupByCampaigns routes tests"""
import pytest

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
            assert ret_val == st_cbc_1

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
            assert ret_val == st_cbc_1

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

            # DELETE
            ret = client.delete(
                f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}",
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 403

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

        # DELETE
        ret = client.delete(
            f"{ST_CLEANUPS_BY_CAMPAIGNS_URL}{st_cbc_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
