"""Timeseries by campaign routes tests"""
import contextlib

import pytest

from tests.common import AuthTestConfig, AuthHeader


DUMMY_ID = "69"

TIMESERIES_BY_CAMPAIGNS_URL = "/timeseriesbycampaigns/"
TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL = "/timeseriesbycampaignsbyusers/"
CAMPAIGNS_URL = '/campaigns/'


class TestTimeseriesByCampaignsByUsersApi:

    def test_timeseries_by_campaigns_by_users_api(
        self, app, users, timeseries_by_campaigns
    ):

        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]
        tbc_1_id, tbc_2_id = timeseries_by_campaigns

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # POST
        tbcbu_1 = {
            "user_id": user_1_id,
            "timeseries_by_campaign_id": tbc_1_id,
        }
        ret = client.post(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL, json=tbcbu_1)
        assert ret.status_code == 201
        ret_val = ret.json
        tbcbu_1_id = ret_val.pop("id")
        tbcbu_1_etag = ret.headers["ETag"]

        # POST violating unique constraint
        ret = client.post(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL, json=tbcbu_1)
        assert ret.status_code == 409

        # DELETE Timeseries x Campaign association violating fkey constraint
        ret = client.delete(f"{TIMESERIES_BY_CAMPAIGNS_URL}{tbc_1_id}")
        assert ret.status_code == 409

        # GET list
        ret = client.get(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == tbcbu_1_id

        # GET by id
        ret = client.get(f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{tbcbu_1_id}")
        assert ret.status_code == 200
        assert ret.headers["ETag"] == tbcbu_1_etag

        # POST
        tbcbu_2 = {
            "user_id": user_2_id,
            "timeseries_by_campaign_id": tbc_2_id,
        }
        ret = client.post(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL, json=tbcbu_2)
        assert ret.status_code == 201
        ret_val = ret.json
        tbcbu_2_id = ret_val.pop("id")

        # GET list (filtered)
        ret = client.get(
            TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL,
            query_string={"timeseries_by_campaign_id": tbc_1_id}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == tbcbu_1_id
        assert ret_val[0]["timeseries_by_campaign_id"] == tbc_1_id
        assert ret_val[0]["user_id"] == user_1_id
        ret = client.get(
            TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL,
            query_string={"timeseries_by_campaign_id": tbc_2_id}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == tbcbu_2_id
        assert ret_val[0]["timeseries_by_campaign_id"] == tbc_2_id
        assert ret_val[0]["user_id"] == user_2_id
        ret = client.get(
            TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL,
            query_string={
                "timeseries_by_campaign_id": tbc_1_id,
                "user_id": user_2_id,
            }
        )
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 0

        # DELETE wrong ID -> 404
        ret = client.delete(
            f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{DUMMY_ID}"
        )
        assert ret.status_code == 404

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{tbcbu_1_id}"
        )
        assert ret.status_code == 204
        ret = client.delete(
            f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{tbcbu_2_id}"
        )
        assert ret.status_code == 204

        # GET list
        ret = client.get(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 0

        # GET by id -> 404
        ret = client.get(f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{tbcbu_1_id}")
        assert ret.status_code == 404

    @pytest.mark.parametrize(
        "app", (AuthTestConfig, ), indirect=True
    )
    def test_timeseries_by_campaigns_by_users_as_admin_api(
        self, app, users, timeseries_by_campaigns
    ):

        user_1_id = users["Active"]["id"]
        tbc_1_id, _ = timeseries_by_campaigns

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tbcbu_1 = {
                "user_id": user_1_id,
                "timeseries_by_campaign_id": tbc_1_id,
            }
            ret = client.post(
                TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL, json=tbcbu_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tbcbu_1_id = ret_val.pop("id")
            tbcbu_1_etag = ret.headers["ETag"]

            # GET list
            ret = client.get(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbcbu_1_id

            # GET by id
            ret = client.get(
                f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{tbcbu_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tbcbu_1_etag

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{tbcbu_1_id}"
            )
            assert ret.status_code == 204

    @pytest.mark.parametrize(
        "app", (AuthTestConfig, ), indirect=True
    )
    @pytest.mark.parametrize("user", ("user", "anonym"))
    def test_timeseries_by_campaigns_by_users_as_user_or_anonym_api(
        self, app, user, users,
        timeseries_by_campaigns, timeseries_by_campaigns_by_users
    ):
        user_1_id = users["Active"]["id"]
        tbc_1_id, _ = timeseries_by_campaigns
        tbcbu_1_id, _ = timeseries_by_campaigns_by_users

        if user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
            status_code = 403
        else:
            auth_context = contextlib.nullcontext()
            status_code = 401

        client = app.test_client()

        with auth_context:

            # GET list
            ret = client.get(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL)
            assert ret.status_code == status_code

            # POST
            tbcbu = {
                "user_id": user_1_id,
                "timeseries_by_campaign_id": tbc_1_id,
            }
            ret = client.post(
                TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL, json=tbcbu)
            assert ret.status_code == status_code

            # GET list
            ret = client.get(TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL)
            assert ret.status_code == status_code

            # GET by id
            ret = client.get(
                f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{tbcbu_1_id}")
            assert ret.status_code == status_code

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_CAMPAIGNS_BY_USERS_URL}{tbcbu_1_id}"
            )
            assert ret.status_code == status_code


class TestTimeseriesByCampaignByUserForCampaignApi:

    @pytest.mark.parametrize(
        "app", (AuthTestConfig, ), indirect=True
    )
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("timeseries_data")
    @pytest.mark.usefixtures("users_by_campaigns")
    def test_timeseries_by_campaign_by_user_for_campaign_api(
        self, app, user, users, campaigns, timeseries_by_campaigns_by_users
    ):
        campaign_1_id, _ = campaigns
        tbcbu_1_id, _ = timeseries_by_campaigns_by_users

        if user == "admin":
            creds = users["Chuck"]["creds"]
            auth_context = AuthHeader(creds)
        elif user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
        else:
            auth_context = contextlib.nullcontext()

        client = app.test_client()

        with auth_context:

            # GET list
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_1_id}"
                "/timeseriesbycampaignsbyusers/")
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_val = ret.json
                assert len(ret_val) == 1
                assert ret_val[0]["id"] == tbcbu_1_id

            # GET by id
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_1_id}/"
                f"timeseriesbycampaignsbyusers/{tbcbu_1_id}"
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                assert ret.json["id"] == tbcbu_1_id
