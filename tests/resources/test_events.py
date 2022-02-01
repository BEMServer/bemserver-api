"""Events tests"""
import datetime as dt

import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

EVENT_STATES_URL = "/event_states/"
EVENT_LEVELS_URL = "/event_levels/"
EVENT_CATEGORIES_URL = "/event_categories/"
EVENT_CHANNELS_URL = "/event_channels/"
EVENTS_URL = "/events/"


class TestEventStatesApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_event_states_api_as_admin_or_user(self, app, user, users):

        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.get(EVENT_STATES_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 3
            for x in ret.json:
                assert x["id"] in (
                    "NEW",
                    "ONGOING",
                    "CLOSED",
                )

    def test_event_states_api_as_anonym(self, app):

        client = app.test_client()

        ret = client.get(EVENT_STATES_URL)
        assert ret.status_code == 401


class TestEventLevelsApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_event_levels_api_as_admin_or_user(self, app, user, users):

        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET level list
            ret = client.get(EVENT_LEVELS_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 4
            for x in ret.json:
                assert x["id"] in (
                    "INFO",
                    "WARNING",
                    "ERROR",
                    "CRITICAL",
                )

    def test_event_levels_api_as_anonym(self, app):

        client = app.test_client()

        ret = client.get(EVENT_LEVELS_URL)
        assert ret.status_code == 401


class TestEventCategoriesApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_event_categories_api_as_admin_or_user(self, app, user, users):

        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET category list
            ret = client.get(EVENT_CATEGORIES_URL)
            assert ret.status_code == 200
            assert len(ret.json) > 0

    def test_event_categories_api_as_anonym(self, app):

        client = app.test_client()

        ret = client.get(EVENT_CATEGORIES_URL)
        assert ret.status_code == 401


class TestEventsApi:
    def test_events_api(self, app, users, event_channels):
        ec_1_id = event_channels[0]
        ec_2_id = event_channels[1]
        event_channel_1_id = event_channels[0]
        event_channel_2_id = event_channels[1]
        c1_st = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).isoformat()
        c2_et = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENTS_URL)
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
            ret = client.post(EVENTS_URL, json=tse_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tse_1_id = ret_val.pop("id")
            tse_1_etag = ret.headers["ETag"]

            # POST violating fkey constraint
            tse_1["level"] = "Dummy Level"
            ret = client.post(EVENTS_URL, json=tse_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(EVENTS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tse_1_id

            # GET by id
            ret = client.get(f"{EVENTS_URL}{tse_1_id}")
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
            ret = client.post(EVENTS_URL, json=tse_2)
            assert ret.status_code == 201
            ret_val = ret.json
            tse_2_id = ret_val.pop("id")
            tse_2_etag = ret.headers["ETag"]

            # GET list (filtered)
            ret = client.get(EVENTS_URL, query_string={"channel_id": ec_1_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tse_1_id
            ret = client.get(EVENTS_URL, query_string={"level": "WARNING"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tse_2_id
            ret = client.get(
                EVENTS_URL,
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
                f"{EVENTS_URL}{DUMMY_ID}",
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
                f"{EVENTS_URL}{tse_1_id}",
                headers={"If-Match": tse_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{EVENTS_URL}{tse_2_id}",
                headers={"If-Match": tse_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENTS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{EVENTS_URL}{tse_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("event_channels_by_users")
    def test_events_as_user_api(self, app, users, event_channels, campaigns, events):
        tse_1_id = events[0]
        event_channel_1_id = event_channels[0]
        c1_st = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENTS_URL)
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
            ret = client.post(EVENTS_URL, json=tse)
            assert ret.status_code == 201

            # GET by id
            ret = client.get(f"{EVENTS_URL}{tse_1_id}")
            assert ret.status_code == 200
            tse_1_etag = ret.headers["ETag"]

            # DELETE
            ret = client.delete(
                f"{EVENTS_URL}{tse_1_id}",
                headers={"If-Match": tse_1_etag},
            )
            assert ret.status_code == 204

    def test_events_as_anonym_api(self, app, event_channels, events):
        tse_1_id = events[0]
        event_channel_1_id = event_channels[0]
        c1_st = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()

        client = app.test_client()

        # GET list
        ret = client.get(EVENTS_URL)
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
        ret = client.post(EVENTS_URL, json=tse)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENTS_URL}{tse_1_id}")
        assert ret.status_code == 401

        # DELETE
        # ETag is wrong but we get rejected before ETag check anyway
        ret = client.delete(
            f"{EVENTS_URL}{tse_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401
