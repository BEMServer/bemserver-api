"""Timeseries by campaign routes tests"""
import pytest


DUMMY_ID = "69"

TIMESERIES_BY_CAMPAIGNS_URL = "/timeseriesbycampaigns/"


class TestTimeseriesByCampaignsApi:

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 0}, ),
            indirect=True
    )
    def test_timeseries_by_campaigns_api(
        self, app, timeseries_data, campaigns
    ):

        ts_1_id, _, _, _ = timeseries_data[0]
        ts_2_id, _, _, _ = timeseries_data[1]
        campaign_1_id, campaign_2_id = campaigns

        client = app.test_client()

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
            TIMESERIES_BY_CAMPAIGNS_URL,
            query_string={"timeseries_id": ts_1_id}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == tbc_1_id
        assert ret_val[0]["timeseries_id"] == ts_1_id
        assert ret_val[0]["campaign_id"] == ts_1_id
        ret = client.get(
            TIMESERIES_BY_CAMPAIGNS_URL,
            query_string={"campaign_id": campaign_2_id}
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
            }
        )
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 0

        # DELETE wrong ID -> 404
        ret = client.delete(f"{TIMESERIES_BY_CAMPAIGNS_URL}{DUMMY_ID}")
        assert ret.status_code == 404

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
