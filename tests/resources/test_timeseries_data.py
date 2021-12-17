"""Timeseries data tests"""
import contextlib
import io
import datetime as dt

import pytest

from tests.common import AuthHeader

TIMESERIES_DATA_URL = "/timeseries-data/"
CAMPAIGNS_URL = "/campaigns/"


class TestTimeseriesDataForCampaignApi:
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_campaigns")
    @pytest.mark.usefixtures("timeseries_by_campaigns")
    def test_timeseries_data_for_campaign_get(
        self,
        app,
        user,
        users,
        campaigns,
        timeseries,
        timeseries_data,
    ):
        start_time, end_time = timeseries_data
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        campaign_1_id, campaign_2_id = campaigns

        if user == "admin":
            creds = users["Chuck"]["creds"]
            auth_context = AuthHeader(creds)
        elif user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
        else:
            auth_context = contextlib.nullcontext()

        client = app.test_client()

        with auth_context:

            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [
                        ts_1_id,
                    ],
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200

            # Timeseries not in Campaign
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_2_id}/timeseries_data/",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [
                        ts_1_id,
                    ],
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403

            # User not in Campaign
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_2_id}/timeseries_data/",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [
                        ts_2_id,
                    ],
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 200

            # Time range exceeds Campaign
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/",
                query_string={
                    "start_time": (start_time - dt.timedelta(days=1)).isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [
                        ts_1_id,
                    ],
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_campaigns")
    @pytest.mark.usefixtures("timeseries_by_campaigns")
    def test_timeseries_data_for_campaign_get_aggregate(
        self,
        app,
        user,
        users,
        campaigns,
        timeseries,
        timeseries_data,
    ):
        start_time, end_time = timeseries_data
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        campaign_1_id, campaign_2_id = campaigns

        if user == "admin":
            creds = users["Chuck"]["creds"]
            auth_context = AuthHeader(creds)
        elif user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
        else:
            auth_context = contextlib.nullcontext()

        client = app.test_client()

        with auth_context:

            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_1_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200

            # Timeseries not in Campaign
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_2_id}/timeseries_data/aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_1_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403

            # User not in Campaign
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_2_id}/timeseries_data/aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_2_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 200

            # Time range exceeds Campaign
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/aggregate",
                query_string={
                    "start_time": (start_time - dt.timedelta(days=1)).isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_1_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_campaigns")
    @pytest.mark.usefixtures("timeseries_by_campaigns")
    def test_timeseries_data_for_campaign_post(
        self, app, user, users, campaigns, timeseries
    ):

        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        campaign_1_id, campaign_2_id = campaigns

        if user == "admin":
            creds = users["Chuck"]["creds"]
            auth_context = AuthHeader(creds)
        elif user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
        else:
            auth_context = contextlib.nullcontext()

        client = app.test_client()

        with auth_context:

            csv_str = (
                f"Datetime,{ts_1_id}\n"
                "2020-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/",
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 201

            # Timeseries not in Campaign
            csv_str = (
                f"Datetime,{ts_2_id}\n"
                "2020-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/",
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403

            # User not in Campaign
            csv_str = (
                f"Datetime,{ts_2_id}\n"
                "2020-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                f"{CAMPAIGNS_URL}{campaign_2_id}/timeseries_data/",
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 201

            # Time range exceeds Campaign
            csv_str = (
                f"Datetime,{ts_1_id}\n"
                "2019-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/",
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403
