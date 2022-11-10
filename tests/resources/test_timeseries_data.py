"""Timeseries data tests"""
import contextlib
import io

import pytest

from tests.common import AuthHeader

TIMESERIES_DATA_URL = "/timeseries_data/"
DUMMY_ID = "69"


class TestTimeseriesDataApi:
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("for_campaign", (True, False))
    def test_timeseries_data_get(
        self,
        app,
        user,
        users,
        campaigns,
        timeseries,
        timeseries_data,
        for_campaign,
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

            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
                ret_line_1 = "Datetime,1"
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)
                ret_line_1 = "Datetime,Timeseries 0"

            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert ret_csv_lines[0] == ret_line_1
                assert ret_csv_lines[1] == "2020-01-01T00:00:00+0000,0.0"

            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "timezone": "Europe/Paris",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert ret_csv_lines[0] == ret_line_1
                assert ret_csv_lines[1] == "2020-01-01T01:00:00+0100,0.0"

            # User not in Timeseries group
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_2_id,)
                ret_line_1 = "Datetime,2"
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_2_id}/"
                ts_l = (f"Timeseries {ts_2_id-1}",)
                ret_line_1 = "Datetime,Timeseries 1"

            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 200
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert ret_csv_lines[0] == ret_line_1
                assert len(ret_csv_lines) > 1

            # Unknown timezone
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "timezone": "DTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 422

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("for_campaign", (True, False))
    def test_timeseries_data_get_aggregate(
        self,
        app,
        user,
        users,
        campaigns,
        timeseries,
        timeseries_data,
        for_campaign,
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

            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
                ret_line_1 = "Datetime,1"
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)
                ret_line_1 = "Datetime,Timeseries 0"

            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width_value": 1,
                    "bucket_width_unit": "day",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert ret_csv_lines[0] == ret_line_1
                assert len(ret_csv_lines) > 1

            # Set a bucket width value != 1 for a fixed size period
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
                ret_line_1 = "Datetime,1"
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)
                ret_line_1 = "Datetime,Timeseries 0"

            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width_value": 4,
                    "bucket_width_unit": "hour",
                    "timezone": "UTC",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert ret_csv_lines[0] == ret_line_1
                assert len(ret_csv_lines) > 1

            # User not in Timeseries group
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_2_id,)
                ret_line_1 = "Datetime,2"
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_2_id}/"
                ts_l = (f"Timeseries {ts_2_id-1}",)
                ret_line_1 = "Datetime,Timeseries 1"

            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width_value": 1,
                    "bucket_width_unit": "day",
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 200
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert ret_csv_lines[0] == ret_line_1
                assert len(ret_csv_lines) > 1

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("for_campaign", (True, False))
    def test_timeseries_data_post(
        self, app, user, users, campaigns, timeseries, for_campaign
    ):

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

            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                header = f"Datetime,{ts_1_id}\n"
                ts_l = (ts_1_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                header = f"Datetime,Timeseries {ts_1_id-1}\n"
                ts_l = (f"Timeseries {ts_1_id-1}",)

            csv_str = header + (
                "2020-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 201
                ret = client.get(
                    query_url,
                    query_string={
                        "start_time": "2020-01-01T00:00:00+00:00",
                        "end_time": "2020-01-01T03:00:00+00:00",
                        "timeseries": ts_l,
                        "data_state": ds_id,
                    },
                )
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert len(ret_csv_lines) > 1

            # User not in Timeseries group
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                header = f"Datetime,{ts_2_id}\n"
                ts_l = ts_2_id
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_2_id}/"
                header = f"Datetime,Timeseries {ts_2_id-1}\n"
                ts_l = (f"Timeseries {ts_2_id-1}",)

            csv_str = header + (
                "2020-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 201
                ret = client.get(
                    query_url,
                    query_string={
                        "start_time": "2020-01-01T00:00:00+00:00",
                        "end_time": "2020-01-01T03:00:00+00:00",
                        "timeseries": ts_l,
                        "data_state": ds_id,
                    },
                )
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert len(ret_csv_lines) > 1

    @pytest.mark.parametrize("for_campaign", (True, False))
    def test_timeseries_data_post_errors(
        self, app, users, campaigns, timeseries, for_campaign
    ):
        campaign_1_id = campaigns[0]
        ts_1_id = timeseries[0]
        ds_id = 1

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # Unknown campaign
            if for_campaign:
                query_url = TIMESERIES_DATA_URL + f"campaign/{DUMMY_ID}/"
                header = f"Datetime,Timeseries {ts_1_id-1}\n"

                csv_str = header + ("2020-01-01T00:00:00+00:00,0\n")
                ret = client.post(
                    query_url,
                    query_string={
                        "data_state": ds_id,
                    },
                    data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
                )
                assert ret.status_code == 404

            # Unknown data state
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                header = f"Datetime,{ts_1_id}\n"
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                header = f"Datetime,Timeseries {ts_1_id-1}\n"

            csv_str = header + ("2020-01-01T00:00:00+00:00,0\n")
            ret = client.post(
                query_url,
                query_string={
                    "data_state": DUMMY_ID,
                },
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            assert ret.status_code == 422
            assert ret.json["errors"]["query"]["data_state"] == "Unknown data state ID"

            # Unknown timeseries
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                dummy_ts = DUMMY_ID
                header = f"Datetime,{dummy_ts}\n"
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                dummy_ts = "Dummy name"
                header = f"Datetime,{dummy_ts}\n"

            csv_str = header + ("2020-01-01T00:00:00+00:00,0\n")
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            assert ret.status_code == 422
            assert ret.json["message"].startswith(
                "Invalid CSV file content: Unknown timeseries"
            )

            # Invalid CSV content
            csv_str = ""
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"

            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
            )
            assert ret.status_code == 422

            # Invalid TS IDs
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                csv_str = "Datetime,Timeseries 1\n2020-01-01T00:00:00+00:00,0\n"

                ret = client.post(
                    query_url,
                    query_string={
                        "data_state": ds_id,
                    },
                    data={"csv_file": (io.BytesIO(csv_str.encode()), "timeseries.csv")},
                )
                assert ret.status_code == 422

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("for_campaign", (True, False))
    def test_timeseries_data_delete(
        self,
        app,
        user,
        users,
        campaigns,
        timeseries,
        timeseries_data,
        for_campaign,
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

            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)

            if user == "admin":
                # Check there is data before deleting
                ret = client.get(
                    query_url,
                    query_string={
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "timeseries": ts_l,
                        "data_state": ds_id,
                    },
                )
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert len(ret_csv_lines) > 1

            # Delete
            ret = client.delete(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 204
                # Check data is deleted
                ret = client.get(
                    query_url,
                    query_string={
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "timeseries": ts_l,
                        "data_state": ds_id,
                    },
                )
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert len(ret_csv_lines) == 1

            # User not in Timeseries group
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_2_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_2_id}/"
                ts_l = (f"Timeseries {ts_2_id-1}",)

            if user == "admin":
                # Check there is data before deleting
                ret = client.get(
                    query_url,
                    query_string={
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "timeseries": ts_l,
                        "data_state": ds_id,
                    },
                )
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert len(ret_csv_lines) > 1

            # Delete
            ret = client.delete(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 204
                # Check data is deleted
                ret = client.get(
                    query_url,
                    query_string={
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "timeseries": ts_l,
                        "data_state": ds_id,
                    },
                )
                ret_csv_lines = ret.data.decode("utf-8").splitlines()
                assert len(ret_csv_lines) == 1

    @pytest.mark.parametrize("method", ("get", "delete"))
    @pytest.mark.parametrize("for_campaign", (True, False))
    def test_timeseries_data_get_delete_errors(
        self,
        app,
        users,
        campaigns,
        timeseries,
        timeseries_data,
        for_campaign,
        method,
    ):
        start_time, end_time = timeseries_data
        campaign_1_id = campaigns[0]
        ts_1_id = timeseries[0]
        ds_id = 1

        creds = users["Chuck"]["creds"]

        client = app.test_client()
        client_method = getattr(client, method)

        with AuthHeader(creds):

            # Unknown campaign
            if for_campaign:
                query_url = TIMESERIES_DATA_URL + f"campaign/{DUMMY_ID}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)

                ret = client_method(
                    query_url,
                    query_string={
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "timeseries": ts_l,
                        "data_state": ds_id,
                    },
                )
                assert ret.status_code == 404

            # Unknown data state
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)

            ret = client_method(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": DUMMY_ID,
                },
            )
            assert ret.status_code == 422
            assert ret.json["errors"]["query"]["data_state"] == "Unknown data state ID"

            # Unknown timeseries
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (DUMMY_ID,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = ("Dummy name",)

            ret = client_method(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                },
            )
            assert ret.status_code == 422
            assert ret.json["message"].startswith("Unknown timeseries")

    @pytest.mark.parametrize("for_campaign", (True, False))
    def test_timeseries_data_get_aggregate_errors(
        self,
        app,
        users,
        campaigns,
        timeseries,
        timeseries_data,
        for_campaign,
    ):
        start_time, end_time = timeseries_data
        campaign_1_id = campaigns[0]
        ts_1_id = timeseries[0]
        ds_id = 1

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # Unknown campaign
            if for_campaign:
                query_url = TIMESERIES_DATA_URL + f"campaign/{DUMMY_ID}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)

                ret = client.get(
                    f"{query_url}aggregate",
                    query_string={
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "timeseries": ts_l,
                        "data_state": ds_id,
                        "bucket_width_value": 1,
                        "bucket_width_unit": "day",
                    },
                )
                assert ret.status_code == 404

            # Unknown data state
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)

            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": DUMMY_ID,
                    "bucket_width_value": 1,
                    "bucket_width_unit": "day",
                },
            )
            assert ret.status_code == 422
            assert ret.json["errors"]["query"]["data_state"] == "Unknown data state ID"

            # Unknown timeseries
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (DUMMY_ID,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = ("Dummy name",)

            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width_value": 1,
                    "bucket_width_unit": "day",
                },
            )
            assert ret.status_code == 422
            assert ret.json["message"].startswith("Unknown timeseries")

            # Unknown aggregation method
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)

            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width_value": 1,
                    "bucket_width_unit": "day",
                    "aggregation": "dummy",
                },
            )
            assert ret.status_code == 422

            # Unknown timezone
            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width_value": 1,
                    "bucket_width_unit": "day",
                    "timezone": "DTC",
                },
            )
            assert ret.status_code == 422

            # Unknown bucket width unit
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)

            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width_value": 1,
                    "bucket_width_unit": "dummy",
                    "aggregation": "avg",
                },
            )
            assert ret.status_code == 422

            # Invalid bucket width valid for non fixed size periods
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                ts_l = (ts_1_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                ts_l = (f"Timeseries {ts_1_id-1}",)

            ret = client.get(
                f"{query_url}aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "bucket_width_value": 2,
                    "bucket_width_unit": "week",
                    "aggregation": "avg",
                },
            )
            assert ret.status_code == 422
