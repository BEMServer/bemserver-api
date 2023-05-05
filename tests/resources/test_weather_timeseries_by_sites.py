"""Weather timeseries by sites routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

WEATHER_TIMESERIES_BY_SITES_URL = "/weather_timeseries_by_sites/"
SITES_URL = "/sites/"


class TestWeatherTimeseriesBySiteApi:
    def test_weather_timeseries_by_sites_api(self, app, users, sites, timeseries):
        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]
        site_2_id = sites[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(WEATHER_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            wtbs_1 = {
                "site_id": site_1_id,
                "timeseries_id": ts_1_id,
                "parameter": "AIR_TEMPERATURE",
                "forecast": False,
            }
            ret = client.post(WEATHER_TIMESERIES_BY_SITES_URL, json=wtbs_1)
            assert ret.status_code == 201
            ret_val = ret.json
            wtbs_1_id = ret_val.pop("id")
            wtbs_1_etag = ret.headers["ETag"]
            assert "id" not in ret_val.pop("timeseries")
            assert ret_val == wtbs_1

            # POST violating unique constraint
            ret = client.post(WEATHER_TIMESERIES_BY_SITES_URL, json=wtbs_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(WEATHER_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == wtbs_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert "id" not in ret_val.pop("timeseries")
            assert ret_val == wtbs_1

            # PUT
            wtbs_1["timeseries_id"] = ts_2_id
            ret = client.put(
                f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}",
                json=wtbs_1,
                headers={"If-Match": wtbs_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            wtbs_1_etag = ret.headers["ETag"]
            assert "id" not in ret_val.pop("timeseries")
            assert ret_val == wtbs_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{WEATHER_TIMESERIES_BY_SITES_URL}{DUMMY_ID}",
                json=wtbs_1,
                headers={"If-Match": wtbs_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            wtbs_2 = {
                "site_id": site_2_id,
                "timeseries_id": ts_2_id,
                "parameter": "RELATIVE_HUMIDITY",
                "forecast": True,
            }
            ret = client.post(WEATHER_TIMESERIES_BY_SITES_URL, json=wtbs_2)
            assert ret.status_code == 201
            ret_val = ret.json
            wtbs_2_id = ret_val.pop("id")
            wtbs_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            wtbs_1["site_id"] = wtbs_2["site_id"]
            wtbs_1["parameter"] = wtbs_2["parameter"]
            wtbs_1["forecast"] = wtbs_2["forecast"]
            ret = client.put(
                f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}",
                json=wtbs_1,
                headers={"If-Match": wtbs_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(WEATHER_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                WEATHER_TIMESERIES_BY_SITES_URL,
                query_string={"site_id": site_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == wtbs_1_id
            ret = client.get(
                WEATHER_TIMESERIES_BY_SITES_URL,
                query_string={"forecast": True},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == wtbs_2_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{WEATHER_TIMESERIES_BY_SITES_URL}{DUMMY_ID}",
                headers={"If-Match": wtbs_1_etag},
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
                f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}",
                headers={"If-Match": wtbs_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_2_id}",
                headers={"If-Match": wtbs_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(WEATHER_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_weather_timeseries_by_sites_as_user_api(
        self,
        app,
        users,
        sites,
        timeseries,
        weather_timeseries_by_sites,
    ):
        user_creds = users["Active"]["creds"]
        site_1_id = sites[0]
        ts_1_id = timeseries[0]
        ts_3_id = timeseries[2]
        wtbs_1_id = weather_timeseries_by_sites[0]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(WEATHER_TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            wtbs_1 = ret_val[0]
            assert "id" not in wtbs_1.pop("timeseries")
            assert wtbs_1.pop("id") == wtbs_1_id

            # POST
            wtbs_3 = {
                "site_id": site_1_id,
                "timeseries_id": ts_1_id,
                "parameter": "AIR_TEMPERATURE",
                "forecast": False,
            }
            ret = client.post(WEATHER_TIMESERIES_BY_SITES_URL, json=wtbs_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}")
            assert ret.status_code == 200
            wtbs_1_etag = ret.headers["ETag"]

            # PUT
            wtbs_1["timeseries_id"] = ts_3_id
            ret = client.put(
                f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}",
                json=wtbs_1,
                headers={"If-Match": wtbs_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}",
                headers={"If-Match": wtbs_1_etag},
            )
            assert ret.status_code == 403

    def test_weather_timeseries_by_sites_as_anonym_api(
        self, app, sites, timeseries, weather_timeseries_by_sites
    ):
        site_1_id = sites[0]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        wtbs_1_id = weather_timeseries_by_sites[0]

        client = app.test_client()

        # GET list
        ret = client.get(WEATHER_TIMESERIES_BY_SITES_URL)
        assert ret.status_code == 401

        # POST
        wtbs_3 = {
            "site_id": site_1_id,
            "timeseries_id": ts_2_id,
            "parameter": "AIR_TEMPERATURE",
            "forecast": False,
        }
        ret = client.post(WEATHER_TIMESERIES_BY_SITES_URL, json=wtbs_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}")
        assert ret.status_code == 401

        # PUT
        wtbs_1 = {
            "site_id": site_1_id,
            "timeseries_id": ts_1_id,
        }
        ret = client.put(
            f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}",
            json=wtbs_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{WEATHER_TIMESERIES_BY_SITES_URL}{wtbs_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
