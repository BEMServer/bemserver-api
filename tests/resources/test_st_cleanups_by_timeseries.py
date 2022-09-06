"""STCleanupByTimeseriess routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ST_CLEANUPS_BY_TIMESERIES_URL = "/st_cleanups_by_timeseries/"


class TestST_CleanupByTimeseriessApi:
    def test_st_cleanups_by_timeseries_api(
        self, app, users, campaigns, st_cleanups_by_timeseries
    ):

        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]
        st_cbt_1_id = st_cleanups_by_timeseries[0]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(ST_CLEANUPS_BY_TIMESERIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list, filtered
            ret = client.get(
                ST_CLEANUPS_BY_TIMESERIES_URL,
                query_string={"campaign_id": campaign_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbt_1_id

            # GET by id
            ret = client.get(f"{ST_CLEANUPS_BY_TIMESERIES_URL}{st_cbt_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val["id"] == st_cbt_1_id

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_st_cleanups_by_timeseries_as_user_api(
        self, app, users, campaigns, st_cleanups_by_timeseries
    ):

        user_creds = users["Active"]["creds"]
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]
        st_cbt_1_id = st_cleanups_by_timeseries[0]
        st_cbt_2_id = st_cleanups_by_timeseries[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(ST_CLEANUPS_BY_TIMESERIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            st_cbt_1 = ret_val[0]
            assert st_cbt_1["id"] == st_cbt_1_id

            # GET list, filtered
            ret = client.get(
                ST_CLEANUPS_BY_TIMESERIES_URL,
                query_string={"campaign_id": campaign_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbt_1_id
            ret = client.get(
                ST_CLEANUPS_BY_TIMESERIES_URL,
                query_string={"campaign_id": campaign_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val

            # GET by id
            ret = client.get(f"{ST_CLEANUPS_BY_TIMESERIES_URL}{st_cbt_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val["id"] == st_cbt_1_id
            ret = client.get(f"{ST_CLEANUPS_BY_TIMESERIES_URL}{st_cbt_2_id}")
            assert ret.status_code == 403

    def test_st_cleanups_by_timeseries_as_anonym_api(
        self, app, st_cleanups_by_timeseries
    ):

        st_cbt_1_id = st_cleanups_by_timeseries[0]

        client = app.test_client()

        # GET list
        ret = client.get(ST_CLEANUPS_BY_TIMESERIES_URL)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{ST_CLEANUPS_BY_TIMESERIES_URL}{st_cbt_1_id}")
        assert ret.status_code == 401
