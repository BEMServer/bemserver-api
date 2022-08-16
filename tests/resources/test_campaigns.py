"""Campaigns routes tests"""
import datetime as dt

import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

CAMPAIGNS_URL = "/campaigns/"


class TestCampaignsApi:
    def test_campaigns_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

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
                "timezone": "Europe/Paris",
            }
            ret = client.post(CAMPAIGNS_URL, json=campaign_1)
            assert ret.status_code == 201
            ret_val = ret.json
            campaign_1_id = ret_val.pop("id")
            campaign_1_etag = ret.headers["ETag"]
            assert ret_val == campaign_1

            # POST violating unique constraint
            ret = client.post(CAMPAIGNS_URL, json=campaign_1)
            assert ret.status_code == 409

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
                headers={"If-Match": campaign_1_etag},
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
                headers={"If-Match": campaign_1_etag},
            )
            assert ret.status_code == 404

            # POST campaign 2
            campaign_2 = {
                "name": "Campaign 2",
                "start_time": (
                    dt.datetime(2016, 4, 8, tzinfo=dt.timezone.utc).isoformat()
                ),
                "end_time": (
                    dt.datetime(2019, 9, 20, tzinfo=dt.timezone.utc).isoformat()
                ),
                "timezone": "UTC",
            }
            ret = client.post(CAMPAIGNS_URL, json=campaign_2)
            ret_val = ret.json
            campaign_2_id = ret_val.pop("id")
            campaign_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            campaign_2["name"] = campaign_1["name"]
            ret = client.put(
                f"{CAMPAIGNS_URL}{campaign_2_id}",
                json=campaign_2,
                headers={"If-Match": campaign_2_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(CAMPAIGNS_URL, query_string={"name": "Campaign 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == campaign_1_id

            # GET sorted list
            ret = client.get(CAMPAIGNS_URL, query_string={"sort": "name"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == campaign_1_id
            assert ret_val[1]["id"] == campaign_2_id
            ret = client.get(CAMPAIGNS_URL, query_string={"sort": "+name"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == campaign_1_id
            assert ret_val[1]["id"] == campaign_2_id
            ret = client.get(CAMPAIGNS_URL, query_string={"sort": "-name"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == campaign_2_id
            assert ret_val[1]["id"] == campaign_1_id

            # GET list using "in_name"
            ret = client.get(CAMPAIGNS_URL, query_string={"in_name": "not"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(CAMPAIGNS_URL, query_string={"in_name": "paign"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == campaign_1_id
            ret = client.get(CAMPAIGNS_URL, query_string={"in_name": "paign 2"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == campaign_2_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{CAMPAIGNS_URL}{DUMMY_ID}", headers={"If-Match": campaign_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{CAMPAIGNS_URL}{campaign_1_id}", headers={"If-Match": campaign_1_etag}
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{CAMPAIGNS_URL}{campaign_2_id}", headers={"If-Match": campaign_2_etag}
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

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_campaigns_as_user_api(self, app, users, campaigns):

        user_creds = users["Active"]["creds"]
        campaign_1_id, campaign_2_id = campaigns

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            campaign_1 = ret_val[0]
            assert campaign_1.pop("id") == campaign_1_id

            # GET list with filters
            ret = client.get(CAMPAIGNS_URL, query_string={"name": "Campaign 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == campaign_1_id
            ret = client.get(CAMPAIGNS_URL, query_string={"name": "Campaign 2"})
            assert ret.status_code == 200
            assert not ret.json

            # GET list using "in_name"
            ret = client.get(CAMPAIGNS_URL, query_string={"in_name": "not"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(CAMPAIGNS_URL, query_string={"in_name": "paign"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == campaign_1_id

            # POST
            campaign_3 = {
                "name": "Campaign 3",
                "start_time": (
                    dt.datetime(2012, 9, 4, tzinfo=dt.timezone.utc).isoformat()
                ),
                "end_time": (
                    dt.datetime(2017, 9, 29, tzinfo=dt.timezone.utc).isoformat()
                ),
                "timezone": "UTC",
            }
            ret = client.post(CAMPAIGNS_URL, json=campaign_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{CAMPAIGNS_URL}{campaign_1_id}")
            assert ret.status_code == 200
            campaign_1_etag = ret.headers["ETag"]

            ret = client.get(f"{CAMPAIGNS_URL}{campaign_2_id}")
            assert ret.status_code == 403

            # PUT
            campaign_1["description"] = "Fantastic campaign"
            ret = client.put(
                f"{CAMPAIGNS_URL}{campaign_1_id}",
                json=campaign_1,
                headers={"If-Match": campaign_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{CAMPAIGNS_URL}{campaign_1_id}", headers={"If-Match": campaign_1_etag}
            )
            assert ret.status_code == 403

    def test_campaigns_as_anonym_api(self, app, campaigns):

        campaign_1_id, _ = campaigns

        client = app.test_client()

        # GET list
        ret = client.get(CAMPAIGNS_URL)
        assert ret.status_code == 401

        # POST
        campaign_3 = {
            "name": "Campaign 3",
            "start_time": (dt.datetime(2012, 9, 4, tzinfo=dt.timezone.utc).isoformat()),
            "end_time": (dt.datetime(2017, 9, 29, tzinfo=dt.timezone.utc).isoformat()),
            "timezone": "UTC",
        }
        ret = client.post(CAMPAIGNS_URL, json=campaign_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{CAMPAIGNS_URL}{campaign_1_id}")
        assert ret.status_code == 401

        # PUT
        campaign_1 = {
            "name": "Super Campaign 1",
        }
        ret = client.put(
            f"{CAMPAIGNS_URL}{campaign_1_id}",
            json=campaign_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{CAMPAIGNS_URL}{campaign_1_id}", headers={"If-Match": "Dummy-Etag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
