"""Energy consumption timeseries by sites routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL = "/energy_consumption_timeseries_by_sites/"
SITES_URL = "/sites/"


class TestEnergyConsumptionTimeseriesBySiteApi:
    def test_energy_consumption_timeseries_by_sites_api(
        self, app, users, sites, timeseries, energy_sources, energy_end_uses
    ):

        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]
        site_2_id = sites[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        energy_source_1_id = energy_sources[1]
        energy_end_use_1_id = energy_end_uses[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ectbs_1 = {
                "site_id": site_1_id,
                "timeseries_id": ts_1_id,
                "source_id": energy_source_1_id,
                "end_use_id": energy_end_use_1_id,
                "wh_conversion_factor": 1,
            }
            ret = client.post(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL, json=ectbs_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ectbs_1_id = ret_val.pop("id")
            ectbs_1_etag = ret.headers["ETag"]
            assert ret_val == ectbs_1

            # POST violating unique constraint
            ret = client.post(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL, json=ectbs_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}"
            )
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ectbs_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == ectbs_1

            # PUT
            ectbs_1["timeseries_id"] = ts_2_id
            ret = client.put(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}",
                json=ectbs_1,
                headers={"If-Match": ectbs_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            ectbs_1_etag = ret.headers["ETag"]
            assert ret_val == ectbs_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{DUMMY_ID}",
                json=ectbs_1,
                headers={"If-Match": ectbs_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            ectbs_2 = {
                "site_id": site_2_id,
                "timeseries_id": ts_2_id,
                "source_id": energy_source_1_id,
                "end_use_id": energy_end_use_1_id,
                "wh_conversion_factor": 1,
            }
            ret = client.post(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL, json=ectbs_2)
            ret_val = ret.json
            ectbs_2_id = ret_val.pop("id")
            ectbs_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            ectbs_1["site_id"] = ectbs_2["site_id"]
            ectbs_1["timeseries_id"] = ectbs_2["timeseries_id"]
            ret = client.put(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}",
                json=ectbs_1,
                headers={"If-Match": ectbs_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL,
                query_string={"site_id": site_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ectbs_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{DUMMY_ID}",
                headers={"If-Match": ectbs_1_etag},
            )
            assert ret.status_code == 404

            # DELETE site cascade
            ret = client.get(f"{SITES_URL}{site_1_id}")
            site_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{SITES_URL}{site_1_id}", headers={"If-Match": site_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}",
                headers={"If-Match": ectbs_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_2_id}",
                headers={"If-Match": ectbs_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}"
            )
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_energy_consumption_timeseries_by_sites_as_user_api(
        self,
        app,
        users,
        sites,
        timeseries,
        energy_sources,
        energy_end_uses,
        energy_consumption_timeseries_by_sites,
    ):

        user_creds = users["Active"]["creds"]
        site_1_id = sites[0]
        ts_1_id = timeseries[0]
        ts_3_id = timeseries[2]
        energy_source_1_id = energy_sources[1]
        energy_end_use_1_id = energy_end_uses[1]
        ectbs_1_id = energy_consumption_timeseries_by_sites[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ectbs_1 = ret_val[0]
            assert ectbs_1.pop("id") == ectbs_1_id

            # POST
            ectbs_3 = {
                "site_id": site_1_id,
                "timeseries_id": ts_1_id,
                "source_id": energy_source_1_id,
                "end_use_id": energy_end_use_1_id,
                "wh_conversion_factor": 1,
            }
            ret = client.post(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL, json=ectbs_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}"
            )
            assert ret.status_code == 200
            ectbs_1_etag = ret.headers["ETag"]

            # PUT
            ectbs_1["timeseries_id"] = ts_3_id
            ret = client.put(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}",
                json=ectbs_1,
                headers={"If-Match": ectbs_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}",
                headers={"If-Match": ectbs_1_etag},
            )
            assert ret.status_code == 403

    def test_energy_consumption_timeseries_by_sites_as_anonym_api(
        self, app, sites, timeseries, energy_consumption_timeseries_by_sites
    ):
        site_1_id = sites[0]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        ectbs_1_id = energy_consumption_timeseries_by_sites[0]

        client = app.test_client()

        # GET list
        ret = client.get(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL)
        assert ret.status_code == 401

        # POST
        ectbs_3 = {
            "site_id": site_1_id,
            "timeseries_id": ts_2_id,
        }
        ret = client.post(ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL, json=ectbs_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}")
        assert ret.status_code == 401

        # PUT
        ectbs_1 = {
            "site_id": site_1_id,
            "timeseries_id": ts_1_id,
        }
        ret = client.put(
            f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}",
            json=ectbs_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{ENERGY_CONSUMPTION_TIMESERIES_BY_SITES_URL}{ectbs_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
