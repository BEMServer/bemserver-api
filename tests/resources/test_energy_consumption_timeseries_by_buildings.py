"""Energy consumption timeseries by buildings routes tests"""

import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL = (
    "/energy_consumption_timeseries_by_buildings/"
)
BUILDINGS_URL = "/buildings/"


class TestEnergyConsumptionTimeseriesByBuildingApi:
    def test_energy_consumption_timeseries_by_buildings_api(
        self, app, users, buildings, timeseries, energies, energy_end_uses
    ):
        creds = users["Chuck"]["creds"]
        building_1_id = buildings[0]
        building_2_id = buildings[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        energy_1_id = energies[1]
        energy_end_use_1_id = energy_end_uses[1]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ectbb_1 = {
                "building_id": building_1_id,
                "timeseries_id": ts_1_id,
                "energy_id": energy_1_id,
                "end_use_id": energy_end_use_1_id,
            }
            ret = client.post(
                ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL, json=ectbb_1
            )
            assert ret.status_code == 201
            ret_val = ret.json
            ectbb_1_id = ret_val.pop("id")
            ectbb_1_etag = ret.headers["ETag"]
            assert "id" not in ret_val.pop("timeseries")
            assert ret_val == ectbb_1

            # POST violating unique constraint
            ret = client.post(
                ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL, json=ectbb_1
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}"
            )
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ectbb_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert "id" not in ret_val.pop("timeseries")
            assert ret_val == ectbb_1

            # PUT
            ectbb_1["timeseries_id"] = ts_2_id
            ret = client.put(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}",
                json=ectbb_1,
                headers={"If-Match": ectbb_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            ectbb_1_etag = ret.headers["ETag"]
            assert "id" not in ret_val.pop("timeseries")
            assert ret_val == ectbb_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{DUMMY_ID}",
                json=ectbb_1,
                headers={"If-Match": ectbb_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            ectbb_2 = {
                "building_id": building_2_id,
                "timeseries_id": ts_2_id,
                "energy_id": energy_1_id,
                "end_use_id": energy_end_use_1_id,
            }
            ret = client.post(
                ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL, json=ectbb_2
            )
            ret_val = ret.json
            ectbb_2_id = ret_val.pop("id")
            ectbb_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            ectbb_1["building_id"] = ectbb_2["building_id"]
            ectbb_1["timeseries_id"] = ectbb_2["timeseries_id"]
            ret = client.put(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}",
                json=ectbb_1,
                headers={"If-Match": ectbb_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL,
                query_string={"building_id": building_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ectbb_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{DUMMY_ID}",
                headers={"If-Match": ectbb_1_etag},
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
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}",
                headers={"If-Match": ectbb_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_2_id}",
                headers={"If-Match": ectbb_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}"
            )
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_energy_consumption_timeseries_by_buildings_as_user_api(
        self,
        app,
        users,
        buildings,
        timeseries,
        energies,
        energy_end_uses,
        energy_consumption_timeseries_by_buildings,
    ):
        user_creds = users["Active"]["creds"]
        building_1_id = buildings[0]
        ts_1_id = timeseries[0]
        ts_3_id = timeseries[2]
        energy_1_id = energies[1]
        energy_end_use_1_id = energy_end_uses[1]
        ectbb_1_id = energy_consumption_timeseries_by_buildings[0]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ectbb_1 = ret_val[0]
            assert "id" not in ectbb_1.pop("timeseries")
            assert ectbb_1.pop("id") == ectbb_1_id

            # POST
            ectbb_3 = {
                "building_id": building_1_id,
                "timeseries_id": ts_1_id,
                "energy_id": energy_1_id,
                "end_use_id": energy_end_use_1_id,
            }
            ret = client.post(
                ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL, json=ectbb_3
            )
            assert ret.status_code == 403

            # GET by id
            ret = client.get(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}"
            )
            assert ret.status_code == 200
            ectbb_1_etag = ret.headers["ETag"]

            # PUT
            ectbb_1["timeseries_id"] = ts_3_id
            ret = client.put(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}",
                json=ectbb_1,
                headers={"If-Match": ectbb_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}",
                headers={"If-Match": ectbb_1_etag},
            )
            assert ret.status_code == 403

    def test_energy_consumption_timeseries_by_buildings_as_anonym_api(
        self, app, buildings, timeseries, energy_consumption_timeseries_by_buildings
    ):
        building_1_id = buildings[0]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        ectbb_1_id = energy_consumption_timeseries_by_buildings[0]

        client = app.test_client()

        # GET list
        ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL)
        assert ret.status_code == 401

        # POST
        ectbb_3 = {
            "building_id": building_1_id,
            "timeseries_id": ts_2_id,
        }
        ret = client.post(ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL, json=ectbb_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(
            f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}"
        )
        assert ret.status_code == 401

        # PUT
        ectbb_1 = {
            "building_id": building_1_id,
            "timeseries_id": ts_1_id,
        }
        ret = client.put(
            f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}",
            json=ectbb_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{ENERGY_CONSUMPTION_TIMESERIES_BY_BUILDINGS_URL}{ectbb_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
