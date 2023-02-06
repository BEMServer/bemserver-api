"""Timeseries by zones routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_BY_ZONES_URL = "/timeseries_by_zones/"
ZONES_URL = "/zones/"


class TestTimeseriesByZoneApi:
    def test_timeseries_by_zones_api(self, app, users, zones, timeseries):
        creds = users["Chuck"]["creds"]
        zone_1_id = zones[0]
        zone_2_id = zones[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(TIMESERIES_BY_ZONES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tbz_1 = {
                "zone_id": zone_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_ZONES_URL, json=tbz_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tbz_1_id = ret_val.pop("id")
            assert ret_val.pop("zone")["name"] == "Zone 1"
            assert ret_val == tbz_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_BY_ZONES_URL, json=tbz_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_BY_ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val.pop("zone")["name"] == "Zone 1"
            assert ret_val == tbz_1

            # POST sep 2
            tbz_2 = {
                "zone_id": zone_2_id,
                "timeseries_id": ts_2_id,
            }
            ret = client.post(TIMESERIES_BY_ZONES_URL, json=tbz_2)
            ret_val = ret.json
            tbz_2_id = ret_val.pop("id")

            # GET list
            ret = client.get(TIMESERIES_BY_ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                TIMESERIES_BY_ZONES_URL,
                query_string={"zone_id": zone_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbz_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{TIMESERIES_BY_ZONES_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE zone cascade
            ret = client.get(f"{ZONES_URL}{zone_1_id}")
            zone_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{ZONES_URL}{zone_1_id}", headers={"If-Match": zone_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}")
            assert ret.status_code == 404
            ret = client.delete(f"{TIMESERIES_BY_ZONES_URL}{tbz_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_BY_ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_timeseries_by_zones_as_user_api(
        self, app, users, zones, timeseries, timeseries_by_zones
    ):
        user_creds = users["Active"]["creds"]
        zone_1_id = zones[0]
        ts_1_id = timeseries[0]
        tbz_1_id = timeseries_by_zones[0]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(TIMESERIES_BY_ZONES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            tbz_1 = ret_val[0]
            assert tbz_1.pop("id") == tbz_1_id

            # POST
            tbz_3 = {
                "zone_id": zone_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_ZONES_URL, json=tbz_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}")
            assert ret.status_code == 200

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}",
            )
            assert ret.status_code == 403

    def test_timeseries_by_zones_as_anonym_api(
        self, app, zones, timeseries, timeseries_by_zones
    ):
        zone_1_id = zones[0]
        ts_2_id = timeseries[1]
        tbz_1_id = timeseries_by_zones[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_BY_ZONES_URL)
        assert ret.status_code == 401

        # POST
        tbz_3 = {
            "zone_id": zone_1_id,
            "timeseries_id": ts_2_id,
        }
        ret = client.post(TIMESERIES_BY_ZONES_URL, json=tbz_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}")
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
