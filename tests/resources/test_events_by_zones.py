"""Events by zones routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

EVENTS_BY_ZONES_URL = "/events_by_zones/"
EVENTS_URL = "/events/"


class TestEventByZoneApi:
    def test_events_by_zones_api(self, app, users, zones, events):

        creds = users["Chuck"]["creds"]
        event_1_id = events[0]
        event_2_id = events[1]
        zone_1_id = zones[0]
        zone_2_id = zones[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENTS_BY_ZONES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ebz_1 = {
                "event_id": event_1_id,
                "zone_id": zone_1_id,
            }
            ret = client.post(EVENTS_BY_ZONES_URL, json=ebz_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ebz_1_id = ret_val.pop("id")
            ebz_1_etag = ret.headers["ETag"]
            assert ret_val == ebz_1

            # POST violating unique constraint
            ret = client.post(EVENTS_BY_ZONES_URL, json=ebz_1)
            assert ret.status_code == 409

            # POST event + zone from different campaigns
            ebz = {
                "event_id": event_2_id,
                "zone_id": zone_1_id,
            }
            ret = client.post(EVENTS_BY_ZONES_URL, json=ebz)
            assert ret.status_code == 422
            ret_val = ret.json
            assert ret_val["errors"]["json"]["_schema"] == (
                "Event and zone must be in same campaign"
            )

            # GET list
            ret = client.get(EVENTS_BY_ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == zone_1_id

            # GET by id
            ret = client.get(f"{EVENTS_BY_ZONES_URL}{ebz_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ebz_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == ebz_1

            # POST
            ebz_2 = {
                "event_id": event_2_id,
                "zone_id": zone_2_id,
            }
            ret = client.post(EVENTS_BY_ZONES_URL, json=ebz_2)
            ret_val = ret.json
            ebz_2_id = ret_val.pop("id")
            ebz_2_etag = ret.headers["ETag"]

            # GET list
            ret = client.get(EVENTS_BY_ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                EVENTS_BY_ZONES_URL,
                query_string={"event_id": event_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ebz_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{EVENTS_BY_ZONES_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE event cascade
            ret = client.get(f"{EVENTS_URL}{event_1_id}")
            event_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{EVENTS_URL}{event_1_id}", headers={"If-Match": event_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(f"{EVENTS_BY_ZONES_URL}{ebz_1_id}")
            assert ret.status_code == 404
            ret = client.delete(
                f"{EVENTS_BY_ZONES_URL}{ebz_2_id}",
                headers={"If-Match": ebz_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENTS_BY_ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{EVENTS_BY_ZONES_URL}{ebz_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_events_by_zones_as_user_api(
        self, app, users, zones, events, events_by_zones
    ):

        user_creds = users["Active"]["creds"]
        event_1_id = events[0]
        event_2_id = events[1]
        zone_1_id = zones[0]
        zone_2_id = zones[1]
        ebz_1_id = events_by_zones[0]
        ebz_2_id = events_by_zones[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(EVENTS_BY_ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ebz_1 = ret_val[0]
            assert ebz_1.pop("id") == ebz_1_id

            # GET by id
            ret = client.get(f"{EVENTS_BY_ZONES_URL}{ebz_1_id}")
            assert ret.status_code == 200

            # GET by id not in campaign scope
            ret = client.get(f"{EVENTS_BY_ZONES_URL}{ebz_2_id}")
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(f"{EVENTS_BY_ZONES_URL}{ebz_1_id}")
            assert ret.status_code == 204

            # POST
            ebz_3 = {
                "event_id": event_1_id,
                "zone_id": zone_1_id,
            }
            ret = client.post(EVENTS_BY_ZONES_URL, json=ebz_3)
            assert ret.status_code == 201
            ret_val = ret.json

            # POST not in campaign scope
            ebz = {
                "event_id": event_2_id,
                "zone_id": zone_2_id,
            }
            ret = client.post(EVENTS_BY_ZONES_URL, json=ebz)
            assert ret.status_code == 403

    def test_events_by_zones_as_anonym_api(self, app, zones, events, events_by_zones):
        event_1_id = events[0]
        zone_2_id = zones[1]
        ebz_1_id = events_by_zones[0]

        client = app.test_client()

        # GET list
        ret = client.get(EVENTS_BY_ZONES_URL)
        assert ret.status_code == 401

        # POST
        ebz_3 = {
            "event_id": event_1_id,
            "zone_id": zone_2_id,
        }
        ret = client.post(EVENTS_BY_ZONES_URL, json=ebz_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENTS_BY_ZONES_URL}{ebz_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{EVENTS_BY_ZONES_URL}{ebz_1_id}")
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
