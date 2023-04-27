"""Sites routes tests"""
import math
import datetime as dt
import json
from unittest.mock import patch

import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal

import pytest

from bemserver_core.model import Timeseries, TimeseriesDataState
from bemserver_core.input_output import tsdio
from bemserver_core.authorization import OpenBar
from bemserver_api.database import db

from tests.common import AuthHeader


DUMMY_ID = "69"

SITES_URL = "/sites/"


class TestSitesApi:
    def test_sites_api(self, app, users, campaigns):
        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            site_1 = {
                "name": "Site 1",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(SITES_URL, json=site_1)
            assert ret.status_code == 201
            ret_val = ret.json
            site_1_id = ret_val.pop("id")
            site_1_etag = ret.headers["ETag"]
            assert ret_val == site_1

            # POST violating unique constraint
            ret = client.post(SITES_URL, json=site_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == site_1_id

            # GET by id
            ret = client.get(f"{SITES_URL}{site_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == site_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == site_1

            # PUT
            site_1["description"] = "Fantastic site"
            site_1_put = site_1.copy()
            del site_1_put["campaign_id"]
            ret = client.put(
                f"{SITES_URL}{site_1_id}",
                json=site_1_put,
                headers={"If-Match": site_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            site_1_etag = ret.headers["ETag"]
            assert ret_val == site_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{SITES_URL}{DUMMY_ID}",
                json=site_1_put,
                headers={"If-Match": site_1_etag},
            )
            assert ret.status_code == 404

            # POST site 2
            site_2 = {
                "name": "Site 2",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(SITES_URL, json=site_2)
            ret_val = ret.json
            site_2_id = ret_val.pop("id")
            site_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            site_1_put["name"] = site_2["name"]
            ret = client.put(
                f"{SITES_URL}{site_1_id}",
                json=site_1_put,
                headers={"If-Match": site_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(SITES_URL, query_string={"name": "Site 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == site_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{SITES_URL}{DUMMY_ID}", headers={"If-Match": site_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{SITES_URL}{site_1_id}", headers={"If-Match": site_1_etag}
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{SITES_URL}{site_2_id}", headers={"If-Match": site_2_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{SITES_URL}{site_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_sites_as_user_api(self, app, users, campaigns, sites):
        user_creds = users["Active"]["creds"]
        campaign_2_id = campaigns[1]
        site_1_id = sites[0]
        site_2_id = sites[1]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            site_1 = ret_val[0]
            assert site_1.pop("id") == site_1_id

            # GET list with filters
            ret = client.get(SITES_URL, query_string={"name": "Site 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == site_1_id
            ret = client.get(SITES_URL, query_string={"name": "Site 2"})
            assert ret.status_code == 200
            assert not ret.json

            # POST
            site_3 = {
                "name": "Site 3",
                "campaign_id": campaign_2_id,
            }
            ret = client.post(SITES_URL, json=site_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{SITES_URL}{site_1_id}")
            assert ret.status_code == 200
            site_1_etag = ret.headers["ETag"]

            ret = client.get(f"{SITES_URL}{site_2_id}")
            assert ret.status_code == 403

            # PUT
            site_1["description"] = "Fantastic site"
            site_1_put = site_1.copy()
            del site_1_put["campaign_id"]
            ret = client.put(
                f"{SITES_URL}{site_1_id}",
                json=site_1_put,
                headers={"If-Match": site_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{SITES_URL}{site_1_id}", headers={"If-Match": site_1_etag}
            )
            assert ret.status_code == 403

    def test_sites_as_anonym_api(self, app, sites, campaigns):
        site_1_id = sites[0]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        # GET list
        ret = client.get(SITES_URL)
        assert ret.status_code == 401

        # POST
        site_3 = {
            "name": "Site 3",
            "campaign_id": campaign_1_id,
        }
        ret = client.post(SITES_URL, json=site_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{SITES_URL}{site_1_id}")
        assert ret.status_code == 401

        # PUT
        site_1 = {
            "name": "Super Site 1",
        }
        ret = client.put(
            f"{SITES_URL}{site_1_id}",
            json=site_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{SITES_URL}{site_1_id}", headers={"If-Match": "Dummy-Etag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401


OIKOLAB_RESPONSE_ATTRIBUTES = {
    "processing_time": 1.89,
    "n_parameter_months": 1,
    "gfs_reference_time": "2023-03-27 00 UTC",
    "next_gfs_update": "in 2.7 hours (approx)",
    "source": "ERA5 (2018) [...]",
    "notes": "GFS forecast data is updated every 6 hours [...]",
}


class TestSitesDownloadWeatherDataApi:
    @pytest.mark.usefixtures("weather_timeseries_by_sites")
    @pytest.mark.parametrize(
        "bsc_config", ({"WEATHER_DATA_CLIENT_API_KEY": "dummy-key"},), indirect=True
    )
    @patch("requests.get")
    def test_sites_download_weather_data_api_as_admin(
        self, mock_get, app, users, sites, timeseries
    ):
        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]

        start_dt = dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
        end_dt = dt.datetime(2020, 1, 1, 2, 0, tzinfo=dt.timezone.utc)
        oik_end_dt = dt.datetime(2020, 1, 1, 1, 0, tzinfo=dt.timezone.utc)

        resp_data = {
            "columns": [
                "coordinates (lat,lon)",
                "model (name)",
                "model elevation (surface)",
                "utc_offset (hrs)",
                "temperature (degC)",
                "relative_humidity (0-1)",
            ],
            "index": [f"{start_dt.timestamp():0.0f}", f"{oik_end_dt.timestamp():0.0f}"],
            "data": [
                ["(43.47394, -1.50940)", "era5", 694.09, 1.0, 2.45, 0.78],
                ["(43.47394, -1.50940)", "era5", 694.09, 1.0, 2.59, 0.78],
            ],
        }
        resp_json = {
            "attributes": OIKOLAB_RESPONSE_ATTRIBUTES,
            "data": json.dumps(resp_data),
        }

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = resp_json

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.put(
                f"{SITES_URL}{site_1_id}/download_weather_data",
                query_string={
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                },
            )
            assert ret.status_code == 204

        mock_get.assert_called_with(
            url="https://api.oikolab.com/weather",
            params={
                "param": ["temperature"],
                "lat": 43.47394,
                "lon": -1.50940,
                "start": start_dt.isoformat(),
                "end": oik_end_dt.isoformat(),
                "api-key": "dummy-key",
            },
            timeout=60,
        )

        with OpenBar():
            air_temp_ts = Timeseries.get_by_id(timeseries[0])
            ds_clean = TimeseriesDataState.get(name="Clean").first()
            data_df = tsdio.get_timeseries_data(
                start_dt,
                end_dt,
                (air_temp_ts,),
                ds_clean,
                col_label="name",
            )
        index = pd.DatetimeIndex(
            [
                "2020-01-01T00:00:00+00:00",
                "2020-01-01T01:00:00+00:00",
            ],
            name="timestamp",
            tz="UTC",
        )
        expected_data_df = pd.DataFrame({"Timeseries 0": [2.45, 2.59]}, index=index)
        assert_frame_equal(data_df, expected_data_df, check_names=False)

    @pytest.mark.usefixtures("weather_timeseries_by_sites")
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.parametrize(
        "bsc_config", ({"WEATHER_DATA_CLIENT_API_KEY": "dummy-key"},), indirect=True
    )
    @patch("requests.get")
    def test_sites_download_weather_data_api_as_user(self, mock_get, app, users, sites):
        creds = users["Active"]["creds"]
        site_2_id = sites[1]

        start_dt = dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
        end_dt = dt.datetime(2020, 1, 1, 2, 0, tzinfo=dt.timezone.utc)

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.put(
                f"{SITES_URL}{site_2_id}/download_weather_data",
                query_string={
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                },
            )
        assert ret.status_code == 403
        mock_get.assert_not_called()

    @patch("requests.get")
    def test_sites_download_weather_data_api_as_anonym(self, mock_get, app, sites):
        site_2_id = sites[1]

        start_dt = dt.datetime(2020, 1, 1, 0, 0, tzinfo=dt.timezone.utc)
        end_dt = dt.datetime(2020, 1, 1, 2, 0, tzinfo=dt.timezone.utc)

        client = app.test_client()

        ret = client.put(
            f"{SITES_URL}{site_2_id}/download_weather_data",
            query_string={
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
            },
        )
        assert ret.status_code == 401

    @pytest.mark.usefixtures("weather_timeseries_by_sites")
    def test_sites_download_weather_data_api_errors(self, app, users, sites):
        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]

        start_dt = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        end_dt = dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc)

        client = app.test_client()

        with AuthHeader(creds):
            # Wrong site ID
            ret = client.put(
                f"{SITES_URL}{DUMMY_ID}/download_weather_data",
                query_string={
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                },
            )
            assert ret.status_code == 404

            # Missing weather settings
            ret = client.put(
                f"{SITES_URL}{site_1_id}/download_weather_data",
                query_string={
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                },
            )
            assert ret.status_code == 409
            assert ret.json["message"] == "Missing weather API settings."

            # Missing site coordinates
            ret = client.get(f"{SITES_URL}{site_1_id}")
            site_1_etag = ret.headers["ETag"]
            site_1 = ret.json
            site_1.pop("id")
            del site_1["campaign_id"]
            del site_1["latitude"]
            ret = client.put(
                f"{SITES_URL}{site_1_id}",
                json=site_1,
                headers={"If-Match": site_1_etag},
            )
            ret = client.get(f"{SITES_URL}{site_1_id}")
            ret = client.put(
                f"{SITES_URL}{site_1_id}/download_weather_data",
                query_string={
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                },
            )
            assert ret.status_code == 409
            assert ret.json["message"] == "Missing site coordinates."

    @pytest.mark.usefixtures("weather_timeseries_by_sites")
    @pytest.mark.parametrize(
        "bsc_config", ({"WEATHER_DATA_CLIENT_API_KEY": "dummy-key"},), indirect=True
    )
    @patch("requests.get")
    def test_sites_download_weather_data_api_api_key_error(
        self, mock_get, app, users, sites
    ):
        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]

        start_dt = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        end_dt = dt.datetime(2020, 1, 2, tzinfo=dt.timezone.utc)

        mock_get.return_value.status_code = 401
        mock_get.return_value.text = (
            '{ "statusCode": 401, '
            '"message": "Access denied due to invalid subscription key. '
            'Make sure to provide a valid key for an active subscription." }'
        )

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.put(
                f"{SITES_URL}{site_1_id}/download_weather_data",
                query_string={
                    "start_time": start_dt.isoformat(),
                    "end_time": end_dt.isoformat(),
                },
            )
            assert ret.status_code == 409
            assert ret.json["message"] == "Wrong API key."

    @pytest.mark.parametrize("type_", ("heating", "cooling"))
    @pytest.mark.parametrize("base", (18, 19.5))
    @pytest.mark.parametrize("unit", ("°C", "°F"))
    @pytest.mark.usefixtures("weather_timeseries_by_sites")
    def test_sites_get_degree_days(
        self, app, users, sites, timeseries, type_, base, unit
    ):
        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]

        start_d = dt.date(2020, 1, 1)
        end_d = dt.date(2021, 1, 1)
        post_d = dt.date(2022, 1, 1)

        air_temp_ts_id = timeseries[0]

        if unit == "°F":
            base = base * 9 / 5 + 32

        with OpenBar():
            ds_clean = TimeseriesDataState.get(name="Clean").first()

            index = pd.date_range(
                start_d, end_d, freq="H", tz="UTC", inclusive="left", name="timestamp"
            )
            weather_df = pd.DataFrame(index=index)
            weather_df[air_temp_ts_id] = index.month
            if type_ == "cooling":
                weather_df[air_temp_ts_id] += 20

            # Introduce a bias to check that computation method uses min/max
            weather_df[air_temp_ts_id] += 5
            weather_df[air_temp_ts_id][index.hour == 1] -= 10

            tsdio.set_timeseries_data(weather_df, data_state=ds_clean)
            db.session.commit()

        client = app.test_client()

        with AuthHeader(creds):
            # Daily DD
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "day",
                    "type": type_,
                    "base": base,
                    "unit": unit,
                },
            )
            assert ret.status_code == 200
            ret_data = ret.json

            expected_d_index = pd.date_range(
                "2020-01-01",
                "2021-01-01",
                freq="D",
                tz="UTC",
                inclusive="left",
                name="timestamp",
            )
            month_avg_temp = expected_d_index.month
            if type_ == "cooling":
                month_avg_temp += 20
            if unit == "°F":
                month_avg_temp = month_avg_temp * 9 / 5 + 32
            expected_d = pd.Series(
                (month_avg_temp - base)
                if type_ == "cooling"
                else (base - month_avg_temp),
                index=expected_d_index,
                dtype="float",
            )
            loaded_dd = pd.Series(ret_data["degree_days"])
            loaded_dd.index = pd.DatetimeIndex(loaded_dd.index)
            assert_series_equal(
                loaded_dd,
                expected_d,
                check_index_type=False,
                check_names=False,
                check_freq=False,
            )

            # Monthly DD
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "month",
                    "type": type_,
                    "base": base,
                    "unit": unit,
                },
            )
            assert ret.status_code == 200
            ret_data = ret.json

            expected_m = expected_d.resample("MS").sum()
            loaded_dd = pd.Series(ret_data["degree_days"])
            loaded_dd.index = pd.DatetimeIndex(loaded_dd.index)
            assert_series_equal(
                loaded_dd,
                expected_m,
                check_index_type=False,
                check_names=False,
                check_freq=False,
            )

            # Yearly DD
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "year",
                    "type": type_,
                    "base": base,
                    "unit": unit,
                },
            )
            assert ret.status_code == 200
            ret_data = ret.json

            expected_y = expected_d.resample("AS").sum()
            loaded_dd = pd.Series(ret_data["degree_days"])
            loaded_dd.index = pd.DatetimeIndex(loaded_dd.index)
            assert_series_equal(
                loaded_dd,
                expected_y,
                check_index_type=False,
                check_names=False,
                check_freq=False,
            )

            # Missing data
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": post_d.isoformat(),
                    "period": "day",
                    "type": type_,
                    "base": base,
                    "unit": unit,
                },
            )
            assert ret.status_code == 200
            ret_data = ret.json

            # Check NaN is serialized as None
            assert all(val is not math.nan for val in ret_data["degree_days"].values())
            assert ret_data["degree_days"]["2021-12-31T00:00:00+00:00"] is None

            expected_post_index = pd.date_range(
                "2021-01-01",
                "2022-01-01",
                freq="D",
                tz="UTC",
                inclusive="left",
                name="timestamp",
            )
            expected_post = pd.Series(
                None,
                index=expected_post_index,
                dtype="float",
            )
            loaded_dd = pd.Series(ret_data["degree_days"])
            loaded_dd.index = pd.DatetimeIndex(loaded_dd.index)
            assert_series_equal(
                loaded_dd,
                pd.concat((expected_d, expected_post)),
                check_index_type=False,
                check_names=False,
                check_freq=False,
            )

            # Wrong unit
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "day",
                    "unit": "dummy",
                },
            )
            assert ret.status_code == 422
            ret_data = ret.json

            # Incompatible unit
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "day",
                    "unit": "Wh",
                },
            )
            assert ret.status_code == 422
            ret_data = ret.json

            # Undefined site
            ret = client.get(
                f"{SITES_URL}{DUMMY_ID}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "day",
                },
            )
            assert ret.status_code == 404
            ret_data = ret.json

    def test_sites_get_degree_days_missing_temperature_ts(self, app, users, sites):
        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]

        start_d = dt.date(2020, 1, 1)
        end_d = dt.date(2021, 1, 1)

        client = app.test_client()

        with AuthHeader(creds):
            # Daily DD
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "day",
                },
            )
            assert ret.status_code == 409

    @pytest.mark.usefixtures("weather_timeseries_by_sites")
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_sites_get_degree_days_as_user(self, app, users, sites, timeseries):
        creds = users["Active"]["creds"]
        site_1_id = sites[0]
        site_2_id = sites[1]

        start_d = dt.date(2020, 1, 1)
        end_d = dt.date(2021, 1, 1)

        air_temp_ts_id = timeseries[0]

        with OpenBar():
            ds_clean = TimeseriesDataState.get(name="Clean").first()

            index = pd.date_range(
                start_d, end_d, freq="H", tz="UTC", inclusive="left", name="timestamp"
            )
            weather_df = pd.DataFrame(index=index)
            weather_df[air_temp_ts_id] = index.month

            tsdio.set_timeseries_data(weather_df, data_state=ds_clean)
            db.session.commit()

        client = app.test_client()

        with AuthHeader(creds):
            # User in campaign and in air temperature TS campaign scope
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "day",
                    "type": "heating",
                    "base": "18",
                    "unit": "°C",
                },
            )
            assert ret.status_code == 200
            ret_data = ret.json

            expected_d_index = pd.date_range(
                "2020-01-01",
                "2021-01-01",
                freq="D",
                tz="UTC",
                inclusive="left",
                name="timestamp",
            )
            month_avg_temp = expected_d_index.month
            expected_d = pd.Series(
                18 - month_avg_temp,
                index=expected_d_index,
                dtype="float",
            )
            loaded_dd = pd.Series(ret_data["degree_days"])
            loaded_dd.index = pd.DatetimeIndex(loaded_dd.index)
            assert_series_equal(
                loaded_dd,
                expected_d,
                check_index_type=False,
                check_names=False,
                check_freq=False,
            )

            # Wrong campaign: site not found
            ret = client.get(
                f"{SITES_URL}{site_2_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "day",
                },
            )
            assert ret.status_code == 403

    @pytest.mark.usefixtures("weather_timeseries_by_sites")
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_sites_get_degree_days_as_user_wtbs_denied(self, app, users, sites):
        """Air temperature defined but in unauthorized campaign scope"""

        creds = users["Active"]["creds"]
        site_1_id = sites[0]

        start_d = dt.date(2020, 1, 1)
        end_d = dt.date(2021, 1, 1)

        client = app.test_client()

        with AuthHeader(creds):
            # User in campaign but not in air temperature TS campaign scope
            ret = client.get(
                f"{SITES_URL}{site_1_id}/degree_days",
                query_string={
                    "start_date": start_d.isoformat(),
                    "end_date": end_d.isoformat(),
                    "period": "day",
                },
            )
            assert ret.status_code == 409
