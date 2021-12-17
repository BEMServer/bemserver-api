"""Timeseries by campaign routes tests"""
import contextlib

import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_URL = "/timeseries/"
TIMESERIES_BY_CAMPAIGNS_URL = "/timeseriesbycampaigns/"
CAMPAIGNS_URL = "/campaigns/"


class TestTimeseriesByCampaignsApi:
    @pytest.mark.parametrize(
        "timeseries_data", ({"nb_ts": 2, "nb_tsd": 0},), indirect=True
    )
    def test_timeseries_by_campaigns_api(self, app, users, timeseries_data, campaigns):

        ts_1_id, _, _, _ = timeseries_data[0]
        ts_2_id, _, _, _ = timeseries_data[1]
        campaign_1_id, campaign_2_id = campaigns

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tbc_1 = {"campaign_id": campaign_1_id, "timeseries_id": ts_1_id}
            ret = client.post(TIMESERIES_BY_CAMPAIGNS_URL, json=tbc_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tbc_1_id = ret_val.pop("id")
            tbc_1_etag = ret.headers["ETag"]

            # POST violating unique constraint
            ret = client.post(TIMESERIES_BY_CAMPAIGNS_URL, json=tbc_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbc_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_CAMPAIGNS_URL}{tbc_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tbc_1_etag

            # POST
            tbc_2 = {"campaign_id": campaign_2_id, "timeseries_id": ts_2_id}
            ret = client.post(TIMESERIES_BY_CAMPAIGNS_URL, json=tbc_2)
            assert ret.status_code == 201
            ret_val = ret.json
            tbc_2_id = ret_val.pop("id")

            # GET list (filtered)
            ret = client.get(
                TIMESERIES_BY_CAMPAIGNS_URL, query_string={"timeseries_id": ts_1_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbc_1_id
            assert ret_val[0]["timeseries_id"] == ts_1_id
            assert ret_val[0]["campaign_id"] == ts_1_id
            ret = client.get(
                TIMESERIES_BY_CAMPAIGNS_URL, query_string={"campaign_id": campaign_2_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbc_2_id
            assert ret_val[0]["timeseries_id"] == ts_2_id
            assert ret_val[0]["campaign_id"] == ts_2_id
            ret = client.get(
                TIMESERIES_BY_CAMPAIGNS_URL,
                query_string={
                    "timeseries_id": ts_1_id,
                    "campaign_id": campaign_2_id,
                },
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET TS list filtered by campaign
            ret = client.get(
                TIMESERIES_URL, query_string={"campaign_id": campaign_1_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{TIMESERIES_BY_CAMPAIGNS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE TS violating fkey constraint
            ret = client.get(f"{TIMESERIES_URL}{ts_1_id}")
            ts_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{TIMESERIES_URL}{ts_1_id}", headers={"If-Match": ts_1_etag}
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(f"{TIMESERIES_BY_CAMPAIGNS_URL}{tbc_1_id}")
            assert ret.status_code == 204
            ret = client.delete(f"{TIMESERIES_BY_CAMPAIGNS_URL}{tbc_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_BY_CAMPAIGNS_URL}{tbc_1_id}")
            assert ret.status_code == 404

    @pytest.mark.parametrize("user", ("user", "anonym"))
    def test_timeseries_by_campains_as_user_or_anonym_api(
        self, app, user, users, timeseries_data, campaigns, timeseries_by_campaigns
    ):

        ts_1_id, _, _, _ = timeseries_data[0]
        tbc_1_id, _ = timeseries_by_campaigns
        campaign_1_id, _ = campaigns

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
            ret = client.get(TIMESERIES_BY_CAMPAIGNS_URL)
            if user == "user":
                assert ret.status_code == 200
                assert not ret.json
            else:
                assert ret.status_code == status_code

            # POST
            tbc = {"campaign_id": campaign_1_id, "timeseries_id": ts_1_id}
            ret = client.post(TIMESERIES_BY_CAMPAIGNS_URL, json=tbc)
            assert ret.status_code == status_code

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_CAMPAIGNS_URL}{tbc_1_id}")
            assert ret.status_code == status_code

            # DELETE
            ret = client.delete(f"{TIMESERIES_BY_CAMPAIGNS_URL}{tbc_1_id}")
            assert ret.status_code == status_code
