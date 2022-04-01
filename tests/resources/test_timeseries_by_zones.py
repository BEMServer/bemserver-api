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
            tbz_1_etag = ret.headers["ETag"]
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
            assert ret.headers["ETag"] == tbz_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tbz_1

            # PUT
            tbz_1["timeseries_id"] = ts_2_id
            ret = client.put(
                f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}",
                json=tbz_1,
                headers={"If-Match": tbz_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tbz_1_etag = ret.headers["ETag"]
            assert ret_val == tbz_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_BY_ZONES_URL}{DUMMY_ID}",
                json=tbz_1,
                headers={"If-Match": tbz_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            tbz_2 = {
                "zone_id": zone_2_id,
                "timeseries_id": ts_2_id,
            }
            ret = client.post(TIMESERIES_BY_ZONES_URL, json=tbz_2)
            ret_val = ret.json
            tbz_2_id = ret_val.pop("id")
            tbz_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tbz_1["zone_id"] = tbz_2["zone_id"]
            tbz_1["timeseries_id"] = tbz_2["timeseries_id"]
            ret = client.put(
                f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}",
                json=tbz_1,
                headers={"If-Match": tbz_1_etag},
            )
            assert ret.status_code == 409

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
            ret = client.delete(
                f"{TIMESERIES_BY_ZONES_URL}{DUMMY_ID}",
                headers={"If-Match": tbz_1_etag},
            )
            assert ret.status_code == 404

            # DELETE zone cascade
            ret = client.get(f"{ZONES_URL}{zone_1_id}")
            zone_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{ZONES_URL}{zone_1_id}", headers={"If-Match": zone_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}",
                headers={"If-Match": tbz_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{TIMESERIES_BY_ZONES_URL}{tbz_2_id}",
                headers={"If-Match": tbz_2_etag},
            )
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
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_timeseries_by_zones_as_user_api(
        self, app, users, zones, timeseries, timeseries_by_zones
    ):

        user_creds = users["Active"]["creds"]
        zone_1_id = zones[0]
        ts_1_id = timeseries[0]
        ts_3_id = timeseries[2]
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
            tbz_1_etag = ret.headers["ETag"]

            # PUT
            tbz_1["timeseries_id"] = ts_3_id
            ret = client.put(
                f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}",
                json=tbz_1,
                headers={"If-Match": tbz_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}",
                headers={"If-Match": tbz_1_etag},
            )
            assert ret.status_code == 403

    def test_timeseries_by_zones_as_anonym_api(
        self, app, zones, timeseries, timeseries_by_zones
    ):
        zone_1_id = zones[0]
        ts_1_id = timeseries[0]
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

        # PUT
        tbz_1 = {
            "zone_id": zone_1_id,
            "timeseries_id": ts_1_id,
        }
        ret = client.put(
            f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}",
            json=tbz_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_BY_ZONES_URL}{tbz_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
