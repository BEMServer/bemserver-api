"""STCleanupByTimeseriess routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ST_CLEANUPS_BY_TIMESERIES_URL = "/st_cleanups_by_timeseries/"


class TestST_CleanupByTimeseriessApi:
    @pytest.mark.parametrize("timeseries", (10,), indirect=True)
    def test_st_cleanups_by_timeseries_api(
        self, app, users, campaigns, timeseries, st_cleanups_by_timeseries
    ):

        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        ts_7_id = timeseries[6]
        st_cbt_1_id = st_cleanups_by_timeseries[0]
        st_cbt_2_id = st_cleanups_by_timeseries[1]

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

            # GET list (full), sort by timeseries name
            ret = client.get(
                f"{ST_CLEANUPS_BY_TIMESERIES_URL}full",
                query_string={"sort": "+timeseries_name"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 10
            assert ret_val[0]["id"] == st_cbt_1_id
            assert ret_val[0]["timeseries_id"] == ts_1_id
            assert ret_val[0]["last_timestamp"] is None

            # GET list (full), sort by timeseries name and timestamps desc
            ret = client.get(
                f"{ST_CLEANUPS_BY_TIMESERIES_URL}full",
                query_string={"sort": "-last_timestamp,+timeseries_name"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 10
            assert ret_val[0]["id"] == st_cbt_2_id
            assert ret_val[0]["timeseries_id"] == ts_2_id
            assert ret_val[0]["last_timestamp"] == "2020-01-01T00:00:00+00:00"
            assert ret_val[1]["id"] == st_cbt_1_id
            assert ret_val[1]["timeseries_id"] == ts_1_id
            assert ret_val[1]["last_timestamp"] is None
            assert ret_val[6]["id"] is None
            assert ret_val[6]["timeseries_id"] == ts_7_id
            assert ret_val[6]["last_timestamp"] is None

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_st_cleanups_by_timeseries_as_user_api(
        self, app, users, campaigns, timeseries, st_cleanups_by_timeseries
    ):

        user_creds = users["Active"]["creds"]
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]
        ts_1_id = timeseries[0]
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

            # GET list (full), sort by timeseries name
            ret = client.get(
                f"{ST_CLEANUPS_BY_TIMESERIES_URL}full",
                query_string={"sort": "+timeseries_name"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbt_1_id
            assert ret_val[0]["timeseries_id"] == ts_1_id
            assert ret_val[0]["last_timestamp"] is None

            # GET list (full), filter by campaign id
            ret = client.get(
                f"{ST_CLEANUPS_BY_TIMESERIES_URL}full",
                query_string={"campaign_id": campaign_1_id},
            )
            assert ret.status_code == 200
            assert len(ret.json) == 1

            # GET list (full), filter by campaign id
            ret = client.get(
                f"{ST_CLEANUPS_BY_TIMESERIES_URL}full",
                query_string={"campaign_id": campaign_2_id},
            )
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

        # GET list (full)
        ret = client.get(f"{ST_CLEANUPS_BY_TIMESERIES_URL}full")
        assert ret.status_code == 401
