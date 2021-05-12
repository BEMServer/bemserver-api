"""Events tests"""

import datetime as dt


DUMMY_ID = "69"

EVENTS_URL = "/events/"


class TestEventsApi:

    def test_event_states_api(self, app):

        client = app.test_client()

        # GET state list
        ret = client.get(f"{EVENTS_URL}states")
        assert ret.status_code == 200
        assert len(ret.json) == 3
        for x in ret.json:
            assert x["id"] in ("NEW", "ONGOING", "CLOSED",)

    def test_event_levels_api(self, app):

        client = app.test_client()

        # GET level list
        ret = client.get(f"{EVENTS_URL}levels")
        assert ret.status_code == 200
        assert len(ret.json) == 4
        for x in ret.json:
            assert x["id"] in ("INFO", "WARNING", "ERROR", "CRITICAL",)

    def test_event_targets_api(self, app):

        client = app.test_client()

        # GET target list
        ret = client.get(f"{EVENTS_URL}targets")
        assert ret.status_code == 200
        assert len(ret.json) == 6
        for x in ret.json:
            assert x["id"] in (
                "TIMESERIES", "SITE", "BUILDING", "FLOOR", "SPACE", "SENSOR",)

    def test_event_categories_api(self, app):

        client = app.test_client()

        # GET category list
        ret = client.get(f"{EVENTS_URL}categories")
        assert ret.status_code == 200
        assert len(ret.json) > 0

    def test_events_api(self, app):

        client = app.test_client()

        # GET list
        ret = client.get(EVENTS_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # POST
        event_1 = {
            "source": "timestamp-guardian",
            "category": "observation_missing",
            "target_type": "TIMESERIES",
            "target_id": 42,
        }

        ts_before_post = dt.datetime.now(dt.timezone.utc)
        ret = client.post(EVENTS_URL, json=event_1)
        ts_after_post = dt.datetime.now(dt.timezone.utc)
        assert ret.status_code == 201
        ret_val = ret.json
        event_1_id = ret_val.pop("id")
        event_1_etag = ret.headers["ETag"]
        for k, v in event_1.items():
            assert ret_val[k] == v
        assert ret_val["state"] == "NEW"
        assert ret_val["level"] == "ERROR"
        event_1_ts_start = dt.datetime.fromisoformat(
            ret_val["timestamp_start"].replace("Z", "00:00"))
        event_1_ts_last_update = dt.datetime.fromisoformat(
            ret_val["timestamp_last_update"].replace("Z", "00:00"))
        assert event_1_ts_start == event_1_ts_last_update
        assert ts_before_post < event_1_ts_start < ts_after_post
        assert "timestamp_end" not in ret_val

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
        ret_val = ret.json
        ret_val.pop("id")
        for k, v in event_1.items():
            assert ret_val[k] == v
        assert ret_val["state"] == "NEW"

        # PUT extend by id
        ret = client.put(
            f"{EVENTS_URL}{event_1_id}/extend",
            headers={'If-Match': event_1_etag})
        assert ret.status_code == 201
        assert ret.headers["ETag"] != event_1_etag
        event_1_etag = ret.headers["ETag"]
        ret_val = ret.json
        ret_val.pop("id")
        for k, v in event_1.items():
            assert ret_val[k] == v
        assert ret_val["state"] == "ONGOING"
        assert ret_val["timestamp_start"] == event_1_ts_start.isoformat()
        assert "timestamp_end" not in ret_val
        ts_last_update = dt.datetime.fromisoformat(
            ret_val["timestamp_last_update"].replace("Z", "00:00"))
        assert ts_last_update > event_1_ts_last_update
        event_1_ts_last_update = ts_last_update

        # PUT close by id
        ret = client.put(
            f"{EVENTS_URL}{event_1_id}/close",
            headers={'If-Match': event_1_etag})
        assert ret.status_code == 201
        assert ret.headers["ETag"] != event_1_etag
        event_1_etag = ret.headers["ETag"]
        ret_val = ret.json
        ret_val.pop("id")
        for k, v in event_1.items():
            assert ret_val[k] == v
        assert ret_val["state"] == "CLOSED"
        assert ret_val["timestamp_start"] == event_1_ts_start.isoformat()
        assert ret_val["timestamp_end"] == ret_val["timestamp_last_update"]
        ts_last_update = dt.datetime.fromisoformat(
            ret_val["timestamp_last_update"].replace("Z", "00:00"))
        assert ts_last_update > event_1_ts_last_update
        event_1_ts_last_update = ts_last_update

        # PUT close by id -> event is already closed, no update
        ret = client.put(
            f"{EVENTS_URL}{event_1_id}/close",
            headers={'If-Match': event_1_etag})
        assert ret.status_code == 201
        ret_val = ret.json
        ts_last_update = dt.datetime.fromisoformat(
            ret_val["timestamp_last_update"].replace("Z", "00:00"))
        assert ts_last_update == event_1_ts_last_update

        # PUT extend by id -> event is already closed, no extend
        ret = client.put(
            f"{EVENTS_URL}{event_1_id}/extend",
            headers={'If-Match': event_1_etag})
        assert ret.status_code == 400

        # PUT extend by id -> wrong id
        ret = client.put(
            f"{EVENTS_URL}{DUMMY_ID}/extend",
            headers={'If-Match': event_1_etag})
        assert ret.status_code == 404

        # DELETE
        ret = client.delete(
            f"{EVENTS_URL}{event_1_id}", headers={"If-Match": event_1_etag})
        assert ret.status_code == 204

        # GET list
        ret = client.get(EVENTS_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # GET by id -> 404
        ret = client.get(f"{EVENTS_URL}{event_1_id}")
        assert ret.status_code == 404
