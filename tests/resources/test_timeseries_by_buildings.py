"""Timeseries by buildings routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_BY_BUILDINGS_URL = "/timeseries_by_buildings/"
BUILDINGS_URL = "/buildings/"


class TestTimeseriesByBuildingApi:
    def test_timeseries_by_buildings_api(self, app, users, buildings, timeseries):

        creds = users["Chuck"]["creds"]
        building_1_id = buildings[0]
        building_2_id = buildings[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tbb_1 = {
                "building_id": building_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_BUILDINGS_URL, json=tbb_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tbb_1_id = ret_val.pop("id")
            tbb_1_etag = ret.headers["ETag"]
            assert ret_val == tbb_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_BY_BUILDINGS_URL, json=tbb_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tbb_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tbb_1

            # PUT
            tbb_1["timeseries_id"] = ts_2_id
            ret = client.put(
                f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}",
                json=tbb_1,
                headers={"If-Match": tbb_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tbb_1_etag = ret.headers["ETag"]
            assert ret_val == tbb_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_BY_BUILDINGS_URL}{DUMMY_ID}",
                json=tbb_1,
                headers={"If-Match": tbb_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            tbb_2 = {
                "building_id": building_2_id,
                "timeseries_id": ts_2_id,
            }
            ret = client.post(TIMESERIES_BY_BUILDINGS_URL, json=tbb_2)
            ret_val = ret.json
            tbb_2_id = ret_val.pop("id")
            tbb_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tbb_1["building_id"] = tbb_2["building_id"]
            tbb_1["timeseries_id"] = tbb_2["timeseries_id"]
            ret = client.put(
                f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}",
                json=tbb_1,
                headers={"If-Match": tbb_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                TIMESERIES_BY_BUILDINGS_URL,
                query_string={"building_id": building_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbb_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{TIMESERIES_BY_BUILDINGS_URL}{DUMMY_ID}",
                headers={"If-Match": tbb_1_etag},
            )
            assert ret.status_code == 404

            # DELETE building cascade
            ret = client.get(f"{BUILDINGS_URL}{building_1_id}")
            building_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{BUILDINGS_URL}{building_1_id}", headers={"If-Match": building_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}",
                headers={"If-Match": tbb_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_2_id}",
                headers={"If-Match": tbb_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_timeseries_by_buildings_as_user_api(
        self, app, users, buildings, timeseries, timeseries_by_buildings
    ):

        user_creds = users["Active"]["creds"]
        building_1_id = buildings[0]
        ts_1_id = timeseries[0]
        ts_3_id = timeseries[2]
        tbb_1_id = timeseries_by_buildings[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            tbb_1 = ret_val[0]
            assert tbb_1.pop("id") == tbb_1_id

            # POST
            tbb_3 = {
                "building_id": building_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_BUILDINGS_URL, json=tbb_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}")
            assert ret.status_code == 200
            tbb_1_etag = ret.headers["ETag"]

            # PUT
            tbb_1["timeseries_id"] = ts_3_id
            ret = client.put(
                f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}",
                json=tbb_1,
                headers={"If-Match": tbb_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}",
                headers={"If-Match": tbb_1_etag},
            )
            assert ret.status_code == 403

    def test_timeseries_by_buildings_as_anonym_api(
        self, app, buildings, timeseries, timeseries_by_buildings
    ):
        building_1_id = buildings[0]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        tbb_1_id = timeseries_by_buildings[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_BY_BUILDINGS_URL)
        assert ret.status_code == 401

        # POST
        tbb_3 = {
            "building_id": building_1_id,
            "timeseries_id": ts_2_id,
        }
        ret = client.post(TIMESERIES_BY_BUILDINGS_URL, json=tbb_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}")
        assert ret.status_code == 401

        # PUT
        tbb_1 = {
            "building_id": building_1_id,
            "timeseries_id": ts_1_id,
        }
        ret = client.put(
            f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}",
            json=tbb_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_BY_BUILDINGS_URL}{tbb_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
