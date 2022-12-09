"""Timeseries by events routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_BY_EVENTS_URL = "/timeseries_by_events/"
EVENTS_URL = "/events/"


class TestTimeseriesByEventApi:
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_timeseries_by_events_api(self, app, users, events, timeseries):

        creds = users["Chuck"]["creds"]
        event_1_id = events[0]
        event_2_id = events[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_BY_EVENTS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tbs_1 = {
                "event_id": event_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_EVENTS_URL, json=tbs_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tbs_1_id = ret_val.pop("id")
            tbs_1_etag = ret.headers["ETag"]
            assert ret_val == tbs_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_BY_EVENTS_URL, json=tbs_1)
            assert ret.status_code == 409

            # POST event + TS from different campaign scopes
            tbs = {
                "event_id": event_2_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_EVENTS_URL, json=tbs)
            assert ret.status_code == 422
            ret_val = ret.json
            assert ret_val["errors"]["json"]["_schema"] == (
                "Event and timeseries must be in same campaign scope"
            )

            # GET list
            ret = client.get(TIMESERIES_BY_EVENTS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_EVENTS_URL}{tbs_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tbs_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tbs_1

            # POST
            tbs_2 = {
                "event_id": event_2_id,
                "timeseries_id": ts_2_id,
            }
            ret = client.post(TIMESERIES_BY_EVENTS_URL, json=tbs_2)
            ret_val = ret.json
            tbs_2_id = ret_val.pop("id")

            # GET list
            ret = client.get(TIMESERIES_BY_EVENTS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                TIMESERIES_BY_EVENTS_URL,
                query_string={"event_id": event_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbs_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{TIMESERIES_BY_EVENTS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE event cascade
            ret = client.get(f"{EVENTS_URL}{event_1_id}")
            event_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{EVENTS_URL}{event_1_id}", headers={"If-Match": event_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(f"{TIMESERIES_BY_EVENTS_URL}{tbs_1_id}")
            assert ret.status_code == 404
            ret = client.delete(f"{TIMESERIES_BY_EVENTS_URL}{tbs_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_BY_EVENTS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_BY_EVENTS_URL}{tbs_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_timeseries_by_events_as_user_api(
        self, app, users, events, timeseries, timeseries_by_events
    ):

        user_creds = users["Active"]["creds"]
        event_1_id = events[0]
        event_2_id = events[1]
        ts_2_id = timeseries[1]
        ts_3_id = timeseries[2]
        tbs_1_id = timeseries_by_events[0]
        tbs_2_id = timeseries_by_events[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(TIMESERIES_BY_EVENTS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            tbs_1 = ret_val[0]
            assert tbs_1.pop("id") == tbs_1_id

            # POST
            tbs_3 = {
                "event_id": event_1_id,
                "timeseries_id": ts_3_id,
            }
            ret = client.post(TIMESERIES_BY_EVENTS_URL, json=tbs_3)
            assert ret.status_code == 201
            ret_val = ret.json

            # POST not in campaign scope
            tbs = {
                "event_id": event_2_id,
                "timeseries_id": ts_2_id,
            }
            ret = client.post(TIMESERIES_BY_EVENTS_URL, json=tbs)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_EVENTS_URL}{tbs_1_id}")
            assert ret.status_code == 200
            tbs_1_etag = ret.headers["ETag"]

            # GET by id not in campaign scope
            ret = client.get(f"{TIMESERIES_BY_EVENTS_URL}{tbs_2_id}")
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_EVENTS_URL}{tbs_1_id}",
                headers={"If-Match": tbs_1_etag},
            )
            assert ret.status_code == 204

    def test_timeseries_by_events_as_anonym_api(
        self, app, events, timeseries, timeseries_by_events
    ):
        event_1_id = events[0]
        ts_2_id = timeseries[1]
        tbs_1_id = timeseries_by_events[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_BY_EVENTS_URL)
        assert ret.status_code == 401

        # POST
        tbs_3 = {
            "event_id": event_1_id,
            "timeseries_id": ts_2_id,
        }
        ret = client.post(TIMESERIES_BY_EVENTS_URL, json=tbs_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_BY_EVENTS_URL}{tbs_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{TIMESERIES_BY_EVENTS_URL}{tbs_1_id}")
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
