"""Events tests"""
import datetime as dt

import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

EVENTS_URL = "/events/"


class TestEventsApi:
    def test_events_api(
        self, app, users, campaign_scopes, event_categories, event_levels
    ):
        cs_1_id = campaign_scopes[0]
        cs_2_id = campaign_scopes[1]
        ec_1_id = event_categories[0]
        el_1_id = event_levels[0]
        el_2_id = event_levels[1]
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
            event_1 = {
                "campaign_scope_id": cs_1_id,
                "timestamp": c1_st,
                "source": "Event source",
                "category_id": ec_1_id,
                "level_id": el_1_id,
            }
            ret = client.post(EVENTS_URL, json=event_1)
            assert ret.status_code == 201
            ret_val = ret.json
            event_1_id = ret_val.pop("id")
            event_1_etag = ret.headers["ETag"]

            # POST violating fkey constraint
            event = event_1.copy()
            event["level_id"] = DUMMY_ID
            ret = client.post(EVENTS_URL, json=event)
            assert ret.status_code == 409

            # GET list
            ret = client.get(EVENTS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == event_1_id

            # GET by id
            ret = client.get(f"{EVENTS_URL}{event_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == event_1_etag

            # PUT
            event_1["source"] = "Super event source"
            put_event = event_1.copy()
            del put_event["campaign_scope_id"]
            del put_event["timestamp"]
            ret = client.put(
                f"{EVENTS_URL}{event_1_id}",
                json=put_event,
                headers={"If-Match": event_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            event_1_etag = ret.headers["ETag"]
            assert ret_val == event_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{EVENTS_URL}{DUMMY_ID}",
                json=put_event,
                headers={"If-Match": event_1_etag},
            )
            assert ret.status_code == 404

            # POST
            event_2 = {
                "campaign_scope_id": cs_2_id,
                "timestamp": c2_et,
                "source": "Another event source",
                "category_id": ec_1_id,
                "level_id": el_2_id,
            }
            ret = client.post(EVENTS_URL, json=event_2)
            assert ret.status_code == 201
            ret_val = ret.json
            event_2_id = ret_val.pop("id")
            event_2_etag = ret.headers["ETag"]

            # GET list (filtered)
            ret = client.get(EVENTS_URL, query_string={"campaign_scope_id": cs_1_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == event_1_id
            ret = client.get(EVENTS_URL, query_string={"level_id": el_2_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == event_2_id
            ret = client.get(
                EVENTS_URL,
                query_string={
                    "campaign_scope_id": cs_2_id,
                    "level_id": el_1_id,
                },
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(EVENTS_URL, query_string={"timestamp_min": c2_et})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ret = client.get(EVENTS_URL, query_string={"timestamp_max": c1_st})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1

            # GET sorted list
            ret = client.get(EVENTS_URL, query_string={"sort": "timestamp"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == event_1_id
            ret = client.get(EVENTS_URL, query_string={"sort": "-timestamp"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == event_2_id

            # DELETE wrong ID -> 404
            # ETag is wrong but we get rejected before ETag check anyway
            ret = client.delete(
                f"{EVENTS_URL}{DUMMY_ID}",
                headers={"If-Match": "Dummy-ETag"},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{EVENTS_URL}{event_1_id}",
                headers={"If-Match": event_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{EVENTS_URL}{event_2_id}",
                headers={"If-Match": event_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENTS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{EVENTS_URL}{event_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_events_as_user_api(
        self,
        app,
        users,
        campaign_scopes,
        campaigns,
        events,
        event_categories,
        event_levels,
    ):
        event_1_id = events[0]
        cs_1_id = campaign_scopes[0]
        ec_1_id = event_categories[0]
        el_1_id = event_levels[0]
        c1_st = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENTS_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 1

            # POST
            event = {
                "campaign_scope_id": cs_1_id,
                "timestamp": c1_st,
                "source": "Event source",
                "category_id": ec_1_id,
                "level_id": el_1_id,
            }
            ret = client.post(EVENTS_URL, json=event)
            assert ret.status_code == 201

            # GET by id
            ret = client.get(f"{EVENTS_URL}{event_1_id}")
            assert ret.status_code == 200
            event_1_etag = ret.headers["ETag"]

            # DELETE
            ret = client.delete(
                f"{EVENTS_URL}{event_1_id}",
                headers={"If-Match": event_1_etag},
            )
            assert ret.status_code == 204

    def test_events_as_anonym_api(
        self, app, campaign_scopes, events, event_categories, event_levels
    ):
        event_1_id = events[0]
        cs_1_id = campaign_scopes[0]
        ec_1_id = event_categories[0]
        el_1_id = event_levels[0]
        c1_st = dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc).isoformat()

        client = app.test_client()

        # GET list
        ret = client.get(EVENTS_URL)
        assert ret.status_code == 401

        # POST
        event = {
            "campaign_scope_id": cs_1_id,
            "timestamp": c1_st,
            "source": "Event source",
            "category_id": ec_1_id,
            "level_id": el_1_id,
        }
        ret = client.post(EVENTS_URL, json=event)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENTS_URL}{event_1_id}")
        assert ret.status_code == 401

        # DELETE
        # ETag is wrong but we get rejected before ETag check anyway
        ret = client.delete(
            f"{EVENTS_URL}{event_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        assert ret.status_code == 401
