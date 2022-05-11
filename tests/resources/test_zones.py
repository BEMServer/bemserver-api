"""Zones routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ZONES_URL = "/zones/"


class TestZonesApi:
    def test_zones_api(self, app, users, campaigns):

        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(ZONES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            zone_1 = {
                "name": "Zone 1",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(ZONES_URL, json=zone_1)
            assert ret.status_code == 201
            ret_val = ret.json
            zone_1_id = ret_val.pop("id")
            zone_1_etag = ret.headers["ETag"]
            assert ret_val == zone_1

            # POST violating unique constraint
            ret = client.post(ZONES_URL, json=zone_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == zone_1_id

            # GET by id
            ret = client.get(f"{ZONES_URL}{zone_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == zone_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == zone_1

            # PUT
            zone_1["description"] = "Fantastic zone"
            zone_1_put = zone_1.copy()
            del zone_1_put["campaign_id"]
            ret = client.put(
                f"{ZONES_URL}{zone_1_id}",
                json=zone_1_put,
                headers={"If-Match": zone_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            zone_1_etag = ret.headers["ETag"]
            assert ret_val == zone_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{ZONES_URL}{DUMMY_ID}",
                json=zone_1_put,
                headers={"If-Match": zone_1_etag},
            )
            assert ret.status_code == 404

            # POST zone 2
            zone_2 = {
                "name": "Zone 2",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(ZONES_URL, json=zone_2)
            ret_val = ret.json
            zone_2_id = ret_val.pop("id")
            zone_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            zone_1_put["name"] = zone_2["name"]
            ret = client.put(
                f"{ZONES_URL}{zone_1_id}",
                json=zone_1_put,
                headers={"If-Match": zone_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(ZONES_URL, query_string={"name": "Zone 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == zone_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{ZONES_URL}{DUMMY_ID}", headers={"If-Match": zone_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{ZONES_URL}{zone_1_id}", headers={"If-Match": zone_1_etag}
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{ZONES_URL}{zone_2_id}", headers={"If-Match": zone_2_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{ZONES_URL}{zone_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_zones_as_user_api(self, app, users, campaigns, zones):

        user_creds = users["Active"]["creds"]
        campaign_2_id = campaigns[1]
        zone_1_id = zones[0]
        zone_2_id = zones[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            zone_1 = ret_val[0]
            assert zone_1.pop("id") == zone_1_id

            # GET list with filters
            ret = client.get(ZONES_URL, query_string={"name": "Zone 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == zone_1_id
            ret = client.get(ZONES_URL, query_string={"name": "Zone 2"})
            assert ret.status_code == 200
            assert not ret.json

            # POST
            zone_3 = {
                "name": "Zone 3",
                "campaign_id": campaign_2_id,
            }
            ret = client.post(ZONES_URL, json=zone_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{ZONES_URL}{zone_1_id}")
            assert ret.status_code == 200
            zone_1_etag = ret.headers["ETag"]

            ret = client.get(f"{ZONES_URL}{zone_2_id}")
            assert ret.status_code == 403

            # PUT
            zone_1["description"] = "Fantastic zone"
            zone_1_put = zone_1.copy()
            del zone_1_put["campaign_id"]
            ret = client.put(
                f"{ZONES_URL}{zone_1_id}",
                json=zone_1_put,
                headers={"If-Match": zone_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{ZONES_URL}{zone_1_id}", headers={"If-Match": zone_1_etag}
            )
            assert ret.status_code == 403

    def test_zones_as_anonym_api(self, app, zones, campaigns):

        zone_1_id = zones[0]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        # GET list
        ret = client.get(ZONES_URL)
        assert ret.status_code == 401

        # POST
        zone_3 = {
            "name": "Zone 3",
            "campaign_id": campaign_1_id,
        }
        ret = client.post(ZONES_URL, json=zone_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{ZONES_URL}{zone_1_id}")
        assert ret.status_code == 401

        # PUT
        zone_1 = {
            "name": "Super Zone 1",
        }
        ret = client.put(
            f"{ZONES_URL}{zone_1_id}",
            json=zone_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{ZONES_URL}{zone_1_id}", headers={"If-Match": "Dummy-Etag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
