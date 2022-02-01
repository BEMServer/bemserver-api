"""Event channels tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

EVENT_CHANNELS_URL = "/event_channels/"
EVENT_CHANNELS_BY_USERS_URL = "/event_channels_by_users/"
EVENT_CHANNELS_BY_CAMPAIGNS_URL = "/event_channels_by_campaigns/"


class TestEventChannelsApi:
    def test_event_channels_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENT_CHANNELS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            event_channel_1 = {
                "name": "Event channel 1",
            }
            ret = client.post(EVENT_CHANNELS_URL, json=event_channel_1)
            assert ret.status_code == 201
            ret_val = ret.json
            event_channel_1_id = ret_val.pop("id")
            event_channel_1_etag = ret.headers["ETag"]
            assert ret_val == event_channel_1

            # GET list
            ret = client.get(EVENT_CHANNELS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == event_channel_1_id

            # GET by id
            ret = client.get(f"{EVENT_CHANNELS_URL}{event_channel_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == event_channel_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == event_channel_1

            # PUT
            event_channel_1["name"] = "Great event channel 1"
            ret = client.put(
                f"{EVENT_CHANNELS_URL}{event_channel_1_id}",
                json=event_channel_1,
                headers={"If-Match": event_channel_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            event_channel_1_etag = ret.headers["ETag"]
            assert ret_val == event_channel_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{EVENT_CHANNELS_URL}{DUMMY_ID}",
                json=event_channel_1,
                headers={"If-Match": event_channel_1_etag},
            )
            assert ret.status_code == 404

            # POST event_channel 2
            event_channel_2 = {
                "name": "Event channel 2",
            }
            ret = client.post(EVENT_CHANNELS_URL, json=event_channel_2)
            ret_val = ret.json
            event_channel_2_id = ret_val.pop("id")
            event_channel_2_etag = ret.headers["ETag"]

            # GET list
            ret = client.get(EVENT_CHANNELS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                EVENT_CHANNELS_URL, query_string={"name": "Great event channel 1"}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == event_channel_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{EVENT_CHANNELS_URL}{DUMMY_ID}",
                headers={"If-Match": event_channel_1_etag},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{EVENT_CHANNELS_URL}{event_channel_1_id}",
                headers={"If-Match": event_channel_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{EVENT_CHANNELS_URL}{event_channel_2_id}",
                headers={"If-Match": event_channel_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENT_CHANNELS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{EVENT_CHANNELS_URL}{event_channel_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("event_channels_by_users")
    def test_event_channels_as_user_api(self, app, users, event_channels):

        user_creds = users["Active"]["creds"]
        event_channel_1_id, event_channel_2_id = event_channels

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(EVENT_CHANNELS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            event_channel_1 = ret_val[0]
            assert event_channel_1.pop("id") == event_channel_1_id

            # GET list with filters
            ret = client.get(
                EVENT_CHANNELS_URL, query_string={"name": "Event channel 1"}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == event_channel_1_id
            ret = client.get(
                EVENT_CHANNELS_URL, query_string={"name": "Event channel 2"}
            )
            assert ret.status_code == 200
            assert not ret.json

            # POST
            event_channel_3 = {
                "name": "Event channel 3",
            }
            ret = client.post(EVENT_CHANNELS_URL, json=event_channel_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{EVENT_CHANNELS_URL}{event_channel_1_id}")
            assert ret.status_code == 200
            event_channel_1_etag = ret.headers["ETag"]

            ret = client.get(f"{EVENT_CHANNELS_URL}{event_channel_2_id}")
            assert ret.status_code == 403

            # PUT
            event_channel_1["name"] = "Great event channel 1"
            ret = client.put(
                f"{EVENT_CHANNELS_URL}{event_channel_1_id}",
                json=event_channel_1,
                headers={"If-Match": event_channel_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{EVENT_CHANNELS_URL}{event_channel_1_id}",
                headers={"If-Match": event_channel_1_etag},
            )
            assert ret.status_code == 403

    def test_event_channels_as_anonym_api(self, app, event_channels):

        event_channel_1_id, _ = event_channels

        client = app.test_client()

        # GET list
        ret = client.get(EVENT_CHANNELS_URL)
        assert ret.status_code == 401

        # POST
        event_channel_3 = {
            "name": "Event channel 3",
        }
        ret = client.post(EVENT_CHANNELS_URL, json=event_channel_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENT_CHANNELS_URL}{event_channel_1_id}")
        assert ret.status_code == 401

        # PUT
        event_channel_1 = {
            "name": "Super Event channel 1",
        }
        ret = client.put(
            f"{EVENT_CHANNELS_URL}{event_channel_1_id}",
            json=event_channel_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{EVENT_CHANNELS_URL}{event_channel_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401


class TestEventChannelsByCampaignsApi:
    def test_event_channels_by_campaigns_api(
        self, app, users, event_channels, campaigns
    ):
        ec_1_id = event_channels[0]
        ec_2_id = event_channels[1]
        campaign_1_id, campaign_2_id = campaigns

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENT_CHANNELS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ecbc_1 = {
                "campaign_id": campaign_1_id,
                "event_channel_id": ec_1_id,
            }
            ret = client.post(EVENT_CHANNELS_BY_CAMPAIGNS_URL, json=ecbc_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ecbc_1_id = ret_val.pop("id")
            ecbc_1_etag = ret.headers["ETag"]

            # POST violating unique constraint
            ret = client.post(EVENT_CHANNELS_BY_CAMPAIGNS_URL, json=ecbc_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(EVENT_CHANNELS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ecbc_1_id

            # GET by id
            ret = client.get(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ecbc_1_etag

            # POST
            ecbc_2 = {
                "campaign_id": campaign_2_id,
                "event_channel_id": ec_2_id,
            }
            ret = client.post(EVENT_CHANNELS_BY_CAMPAIGNS_URL, json=ecbc_2)
            assert ret.status_code == 201
            ret_val = ret.json
            ecbc_2_id = ret_val.pop("id")

            # GET list (filtered)
            ret = client.get(
                EVENT_CHANNELS_BY_CAMPAIGNS_URL,
                query_string={"event_channel_id": ec_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ecbc_1_id
            assert ret_val[0]["event_channel_id"] == ec_1_id
            assert ret_val[0]["campaign_id"] == campaign_1_id
            ret = client.get(
                EVENT_CHANNELS_BY_CAMPAIGNS_URL,
                query_string={"campaign_id": campaign_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ecbc_2_id
            assert ret_val[0]["event_channel_id"] == ec_2_id
            assert ret_val[0]["campaign_id"] == ec_2_id
            ret = client.get(
                EVENT_CHANNELS_BY_CAMPAIGNS_URL,
                query_string={
                    "event_channel_id": ec_1_id,
                    "campaign_id": campaign_2_id,
                },
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET channels list filtered by campaign
            ret = client.get(
                EVENT_CHANNELS_URL, query_string={"campaign_id": campaign_1_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ec_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE channel violating fkey constraint
            ret = client.get(f"{EVENT_CHANNELS_URL}{ec_1_id}")
            ec_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{EVENT_CHANNELS_URL}{ec_1_id}", headers={"If-Match": ec_1_etag}
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_1_id}")
            assert ret.status_code == 204
            ret = client.delete(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENT_CHANNELS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_campaigns")
    def test_event_channel_by_users_as_user_api(
        self, app, users, event_channels, event_channels_by_users
    ):
        ec_1_id = event_channels[0]
        ecbu_1_id = event_channels_by_users[0]
        ecbu_2_id = event_channels_by_users[1]
        user_1_id = users["Active"]["id"]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENT_CHANNELS_BY_USERS_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 1

            # POST
            ecbu = {"user_id": user_1_id, "event_channel_id": ec_1_id}
            ret = client.post(EVENT_CHANNELS_BY_USERS_URL, json=ecbu)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{EVENT_CHANNELS_BY_USERS_URL}{ecbu_1_id}")
            assert ret.status_code == 200

            # GET by id
            ret = client.get(f"{EVENT_CHANNELS_BY_USERS_URL}{ecbu_2_id}")
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(f"{EVENT_CHANNELS_BY_USERS_URL}{ecbu_1_id}")
            assert ret.status_code == 403

    @pytest.mark.usefixtures("users_by_campaigns")
    def test_event_channel_by_users_as_anonym_api(
        self, app, users, event_channels, event_channels_by_users
    ):
        ec_1_id = event_channels[0]
        ecbu_1_id = event_channels_by_users[0]
        user_1_id = users["Active"]["id"]

        client = app.test_client()

        # GET list
        ret = client.get(EVENT_CHANNELS_BY_USERS_URL)
        assert ret.status_code == 401

        # POST
        ecbu = {"user_id": user_1_id, "event_channel_id": ec_1_id}
        ret = client.post(EVENT_CHANNELS_BY_USERS_URL, json=ecbu)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENT_CHANNELS_BY_USERS_URL}{ecbu_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{EVENT_CHANNELS_BY_USERS_URL}{ecbu_1_id}")
        assert ret.status_code == 401

    @pytest.mark.usefixtures("users_by_campaigns")
    def test_event_channel_by_campaigns_as_user_api(
        self, app, users, event_channels, campaigns, event_channels_by_campaigns
    ):
        ec_1_id = event_channels[0]
        ecbc_1_id = event_channels_by_campaigns[0]
        ecbc_2_id = event_channels_by_campaigns[1]
        campaign_1_id = campaigns[0]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENT_CHANNELS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 1

            # POST
            ecbc = {"campaign_id": campaign_1_id, "event_channel_id": ec_1_id}
            ret = client.post(EVENT_CHANNELS_BY_CAMPAIGNS_URL, json=ecbc)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_1_id}")
            assert ret.status_code == 200

            # GET by id
            ret = client.get(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_2_id}")
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_1_id}")
            assert ret.status_code == 403

    @pytest.mark.usefixtures("users_by_campaigns")
    def test_event_channel_by_campaigns_as_anonym_api(
        self, app, users, event_channels, campaigns, event_channels_by_campaigns
    ):
        ec_1_id = event_channels[0]
        ecbc_1_id = event_channels_by_campaigns[0]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        # GET list
        ret = client.get(EVENT_CHANNELS_BY_CAMPAIGNS_URL)
        assert ret.status_code == 401

        # POST
        ecbc = {"campaign_id": campaign_1_id, "event_channel_id": ec_1_id}
        ret = client.post(EVENT_CHANNELS_BY_CAMPAIGNS_URL, json=ecbc)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{EVENT_CHANNELS_BY_CAMPAIGNS_URL}{ecbc_1_id}")
        assert ret.status_code == 401
