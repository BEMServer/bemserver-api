"""Events by buildings routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

EVENTS_BY_BUILDINGS_URL = "/events_by_buildings/"
EVENTS_URL = "/events/"


class TestEventByBuildingApi:
    def test_events_by_buildings_api(self, app, users, buildings, events):

        creds = users["Chuck"]["creds"]
        event_1_id = events[0]
        event_2_id = events[1]
        building_1_id = buildings[0]
        building_2_id = buildings[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENTS_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ebb_1 = {
                "event_id": event_1_id,
                "building_id": building_1_id,
            }
            ret = client.post(EVENTS_BY_BUILDINGS_URL, json=ebb_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ebb_1_id = ret_val.pop("id")
            ebb_1_etag = ret.headers["ETag"]
            assert ret_val == ebb_1

            # POST violating unique constraint
            ret = client.post(EVENTS_BY_BUILDINGS_URL, json=ebb_1)
            assert ret.status_code == 409

            # POST event + building from different campaigns
            ebb = {
                "event_id": event_2_id,
                "building_id": building_1_id,
            }
            ret = client.post(EVENTS_BY_BUILDINGS_URL, json=ebb)
            assert ret.status_code == 422
            ret_val = ret.json
            assert ret_val["errors"]["json"]["_schema"] == (
                "Event and building must be in same campaign"
            )

            # GET list
            ret = client.get(EVENTS_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == building_1_id

            # GET by id
            ret = client.get(f"{EVENTS_BY_BUILDINGS_URL}{ebb_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ebb_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == ebb_1

            # POST
            ebb_2 = {
                "event_id": event_2_id,
                "building_id": building_2_id,
            }
            ret = client.post(EVENTS_BY_BUILDINGS_URL, json=ebb_2)
            ret_val = ret.json
            ebb_2_id = ret_val.pop("id")

            # GET list
            ret = client.get(EVENTS_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                EVENTS_BY_BUILDINGS_URL,
                query_string={"event_id": event_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ebb_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{EVENTS_BY_BUILDINGS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE event cascade
            ret = client.get(f"{EVENTS_URL}{event_1_id}")
            event_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{EVENTS_URL}{event_1_id}", headers={"If-Match": event_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(f"{EVENTS_BY_BUILDINGS_URL}{ebb_1_id}")
            assert ret.status_code == 404
            ret = client.delete(f"{EVENTS_BY_BUILDINGS_URL}{ebb_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENTS_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{EVENTS_BY_BUILDINGS_URL}{ebb_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_events_by_buildings_as_user_api(
        self, app, users, buildings, events, events_by_buildings
    ):

        user_creds = users["Active"]["creds"]
        event_1_id = events[0]
        event_2_id = events[1]
        building_1_id = buildings[0]
        building_2_id = buildings[1]
        ebb_1_id = events_by_buildings[0]
        ebb_2_id = events_by_buildings[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(EVENTS_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ebb_1 = ret_val[0]
            assert ebb_1.pop("id") == ebb_1_id

            # GET by id
            ret = client.get(f"{EVENTS_BY_BUILDINGS_URL}{ebb_1_id}")
            assert ret.status_code == 200

            # GET by id not in campaign scope
            ret = client.get(f"{EVENTS_BY_BUILDINGS_URL}{ebb_2_id}")
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(f"{EVENTS_BY_BUILDINGS_URL}{ebb_1_id}")
            assert ret.status_code == 204

            # POST
            ebb_3 = {
                "event_id": event_1_id,
                "building_id": building_1_id,
            }
            ret = client.post(EVENTS_BY_BUILDINGS_URL, json=ebb_3)
            assert ret.status_code == 201
            ret_val = ret.json

            # POST not in campaign scope
            ebb = {
                "event_id": event_2_id,
                "building_id": building_2_id,
            }
            ret = client.post(EVENTS_BY_BUILDINGS_URL, json=ebb)
            assert ret.status_code == 403

    def test_events_by_buildings_as_anonym_api(
        self, app, buildings, events, events_by_buildings
    ):
        event_1_id = events[0]
        building_2_id = buildings[1]
        ebb_1_id = events_by_buildings[0]

        client = app.test_client()

        # GET list
        ret = client.get(EVENTS_BY_BUILDINGS_URL)
        assert ret.status_code == 401

        # POST
        ebb_3 = {
            "event_id": event_1_id,
            "building_id": building_2_id,
        }
        ret = client.post(EVENTS_BY_BUILDINGS_URL, json=ebb_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENTS_BY_BUILDINGS_URL}{ebb_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{EVENTS_BY_BUILDINGS_URL}{ebb_1_id}")
        assert ret.status_code == 401
