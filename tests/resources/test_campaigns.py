"""Campaigns routes tests"""
import datetime as dt


DUMMY_ID = "69"

CAMPAIGNS_URL = "/campaigns/"


class TestCampaignsApi:

    def test_campaigns_api(self, app):

        client = app.test_client()

        # GET list
        ret = client.get(CAMPAIGNS_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # POST
        campaign_1 = {
            "name": "Campaign 1",
            "start_time": (
                dt.datetime(2012, 9, 4, tzinfo=dt.timezone.utc).isoformat()
            ),
            "end_time": (
                dt.datetime(2017, 9, 29, tzinfo=dt.timezone.utc).isoformat()
            ),
        }

        ret = client.post(CAMPAIGNS_URL, json=campaign_1)
        assert ret.status_code == 201
        ret_val = ret.json
        campaign_1_id = ret_val.pop("id")
        campaign_1_etag = ret.headers["ETag"]
        assert ret_val == campaign_1

        # GET list
        ret = client.get(CAMPAIGNS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == campaign_1_id

        # GET by id
        ret = client.get(f"{CAMPAIGNS_URL}{campaign_1_id}")
        assert ret.status_code == 200
        assert ret.headers["ETag"] == campaign_1_etag
        ret_val = ret.json
        ret_val.pop("id")
        assert ret_val == campaign_1

        # PUT
        campaign_1["description"] = "Fantastic campaign"
        ret = client.put(
            f"{CAMPAIGNS_URL}{campaign_1_id}",
            json=campaign_1,
            headers={"If-Match": campaign_1_etag}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        ret_val.pop("id")
        campaign_1_etag = ret.headers["ETag"]
        assert ret_val == campaign_1

        # PUT wrong ID -> 404
        ret = client.put(
            f"{CAMPAIGNS_URL}{DUMMY_ID}",
            json=campaign_1,
            headers={"If-Match": campaign_1_etag}
        )
        assert ret.status_code == 404

        # DELETE wrong ID -> 404
        ret = client.delete(
            f"{CAMPAIGNS_URL}{DUMMY_ID}",
            headers={"If-Match": campaign_1_etag}
        )
        assert ret.status_code == 404

        # DELETE
        ret = client.delete(
            f"{CAMPAIGNS_URL}{campaign_1_id}",
            headers={"If-Match": campaign_1_etag}
        )
        assert ret.status_code == 204

        # GET list
        ret = client.get(CAMPAIGNS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 0

        # GET by id -> 404
        ret = client.get(f"{CAMPAIGNS_URL}{campaign_1_id}")
        assert ret.status_code == 404
