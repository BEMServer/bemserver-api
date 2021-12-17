"""Timeseries events tests"""
import datetime as dt

import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

CAMPAIGNS_URL = "/campaigns/"
EVENTS_URL = "/events/"
EVENT_CHANNELS_URL = f"{EVENTS_URL}channels/"
TIMESERIES_EVENTS_SUB_URL = "/events/timeseries/"


class TestTimeseriesEventsApi:
    def test_timeseries_events_api(self, app, users, event_channels, campaigns):
        ec_1_id = event_channels[0]
        ec_2_id = event_channels[1]
        campaign_1_id = campaigns[0]
        event_channel_1_id = event_channels[0]
        event_channel_2_id = event_channels[1]
        c1_st = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).isoformat()
        c2_et = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()
        c1_tse_url = f"{CAMPAIGNS_URL}{campaign_1_id}{TIMESERIES_EVENTS_SUB_URL}"

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(c1_tse_url)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tse_1 = {
                "channel_id": event_channel_1_id,
                "timestamp": c1_st,
                "source": "Event source",
                "category": "observation_missing",
                "level": "INFO",
                "state": "NEW",
            }
            ret = client.post(c1_tse_url, json=tse_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tse_1_id = ret_val.pop("id")
            tse_1_etag = ret.headers["ETag"]

            # POST violating fkey constraint
            tse_1["level"] = "Dummy Level"
            ret = client.post(c1_tse_url, json=tse_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(c1_tse_url)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tse_1_id

            # GET by id
            ret = client.get(f"{c1_tse_url}{tse_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tse_1_etag

            # POST
            tse_2 = {
                "channel_id": event_channel_2_id,
                "timestamp": c2_et,
                "source": "Another event source",
                "category": "observation_missing",
                "level": "WARNING",
                "state": "NEW",
            }
            ret = client.post(c1_tse_url, json=tse_2)
            assert ret.status_code == 201
            ret_val = ret.json
            tse_2_id = ret_val.pop("id")
            tse_2_etag = ret.headers["ETag"]

            # GET list (filtered)
            ret = client.get(c1_tse_url, query_string={"channel_id": ec_1_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tse_1_id
            ret = client.get(c1_tse_url, query_string={"level": "WARNING"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tse_2_id
            ret = client.get(
                c1_tse_url,
                query_string={
                    "channel_id": ec_2_id,
                    "level": "INFO",
                },
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # DELETE wrong ID -> 404
            # ETag is wrong but we get rejected before ETag check anyway
            ret = client.delete(
                f"{c1_tse_url}{DUMMY_ID}",
                headers={"If-Match": "Dummy-ETag"},
            )
            assert ret.status_code == 404

            # DELETE channel violating fkey constraint
            ret = client.get(f"{EVENT_CHANNELS_URL}{ec_1_id}")
            ec_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{EVENT_CHANNELS_URL}{ec_1_id}",
                headers={"If-Match": ec_1_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(
                f"{c1_tse_url}{tse_1_id}",
                headers={"If-Match": tse_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{c1_tse_url}{tse_2_id}",
                headers={"If-Match": tse_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(c1_tse_url)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{c1_tse_url}{tse_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_campaigns")
    @pytest.mark.usefixtures("event_channels_by_campaigns")
    def test_timeseries_events_as_user_api(
        self, app, users, event_channels, campaigns, timeseries_events_by_campaigns
    ):
        tse_1_id = timeseries_events_by_campaigns[0]
        tse_2_id = timeseries_events_by_campaigns[1]
        event_channel_1_id = event_channels[0]
        event_channel_2_id = event_channels[1]
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]
        c1_st = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()
        c2_st = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()
        c1_tse_url = f"{CAMPAIGNS_URL}{campaign_1_id}{TIMESERIES_EVENTS_SUB_URL}"
        c2_tse_url = f"{CAMPAIGNS_URL}{campaign_2_id}{TIMESERIES_EVENTS_SUB_URL}"

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(c1_tse_url)
            assert ret.status_code == 200
            assert len(ret.json) == 1

            # POST
            tse = {
                "channel_id": event_channel_1_id,
                "timestamp": c1_st,
                "source": "Event source",
                "category": "observation_missing",
                "level": "INFO",
                "state": "NEW",
            }
            ret = client.post(c1_tse_url, json=tse)
            assert ret.status_code == 201
            tse = {
                "channel_id": event_channel_2_id,
                "timestamp": c2_st,
                "source": "Event source",
                "category": "observation_missing",
                "level": "INFO",
                "state": "NEW",
            }
            ret = client.post(c2_tse_url, json=tse)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{c1_tse_url}{tse_1_id}")
            assert ret.status_code == 200
            tse_1_etag = ret.headers["ETag"]

            # DELETE
            ret = client.delete(
                f"{c1_tse_url}{tse_1_id}",
                headers={"If-Match": tse_1_etag},
            )
            assert ret.status_code == 204

            # GET by id
            ret = client.get(f"{c2_tse_url}{tse_2_id}")
            assert ret.status_code == 403

            # DELETE
            # ETag is wrong but we get rejected before ETag check anyway
            ret = client.delete(
                f"{c2_tse_url}{tse_2_id}",
                headers={"If-Match": tse_1_etag},
            )
            assert ret.status_code == 403

    @pytest.mark.usefixtures("users_by_campaigns")
    @pytest.mark.usefixtures("event_channels_by_campaigns")
    def test_timeseries_events_as_anonym_api(
        self, app, event_channels, campaigns, timeseries_events_by_campaigns
    ):
        tse_1_id = timeseries_events_by_campaigns[0]
        event_channel_1_id = event_channels[0]
        campaign_1_id = campaigns[0]
        c1_st = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()
        c1_tse_url = f"{CAMPAIGNS_URL}{campaign_1_id}{TIMESERIES_EVENTS_SUB_URL}"

        client = app.test_client()

        # GET list
        ret = client.get(c1_tse_url)
        assert ret.status_code == 401

        # POST
        tse = {
            "channel_id": event_channel_1_id,
            "timestamp": c1_st,
            "source": "Event source",
            "category": "observation_missing",
            "level": "INFO",
            "state": "NEW",
        }
        ret = client.post(c1_tse_url, json=tse)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{c1_tse_url}{tse_1_id}")
        assert ret.status_code == 401

        # DELETE
        # ETag is wrong but we get rejected before ETag check anyway
        ret = client.delete(
            f"{c1_tse_url}{tse_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401
