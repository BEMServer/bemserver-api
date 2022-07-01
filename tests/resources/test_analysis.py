"""Analysis tests"""
import contextlib

import pytest

from tests.common import AuthHeader

ANALYSIS_URL = "/analysis/"


class TestAnalysisApi:
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_analysis_completeness(
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
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]
        ds_id = 1

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

            query_url = ANALYSIS_URL + f"campaign/{campaign_1_id}/completeness"
            ts_l = (f"Timeseries {ts_1_id-1}",)

            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width": "1 hour",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == {
                    "timestamps": [
                        "2020-01-01T00:00:00+00:00",
                        "2020-01-01T01:00:00+00:00",
                        "2020-01-01T02:00:00+00:00",
                        "2020-01-01T03:00:00+00:00",
                    ],
                    "timeseries": {
                        "Timeseries 0": {
                            "avg_count": 1.0,
                            "avg_ratio": 1.0,
                            "count": [1, 1, 1, 1],
                            "expected_count": [1.0, 1.0, 1.0, 1.0],
                            "interval": 3600.0,
                            "ratio": [1.0, 1.0, 1.0, 1.0],
                            "total_count": 4,
                            "undefined_interval": True,
                        }
                    },
                }

            # User not in Timeseries group
            query_url = ANALYSIS_URL + f"campaign/{campaign_2_id}/completeness"
            ts_l = (f"Timeseries {ts_2_id-1}",)

            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width": "1 hour",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 200
                ret_data = ret.json
                assert ret_data == {
                    "timestamps": [
                        "2020-01-01T00:00:00+00:00",
                        "2020-01-01T01:00:00+00:00",
                        "2020-01-01T02:00:00+00:00",
                        "2020-01-01T03:00:00+00:00",
                    ],
                    "timeseries": {
                        "Timeseries 1": {
                            "avg_count": 1.0,
                            "avg_ratio": 1.0,
                            "count": [1, 1, 1, 1],
                            "expected_count": [1.0, 1.0, 1.0, 1.0],
                            "interval": 3600.0,
                            "ratio": [1.0, 1.0, 1.0, 1.0],
                            "total_count": 4,
                            "undefined_interval": True,
                        }
                    },
                }
