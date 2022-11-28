"""Timeseries data tests"""
import contextlib

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
    @pytest.mark.parametrize("format_", ("json", "csv"))
    def test_timeseries_data_get(
        self,
        app,
        user,
        users,
        campaigns,
        timeseries,
        timeseries_data,
        for_campaign,
        format_,
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
                headers={"Accept": f"application/{format_}"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                if format_ == "csv":
                    ret_csv_lines = ret.data.decode("utf-8").splitlines()
                    assert ret_csv_lines[0] == ret_line_1
                    assert ret_csv_lines[1] == "2020-01-01T00:00:00+0000,0.0"
                else:
                    assert list(ret.json.keys()) == [str(ts_l[0])]
                    assert ret.json[str(ts_l[0])] == {
                        "2020-01-01T00:00:00+00:00": 0.0,
                        "2020-01-01T01:00:00+00:00": 1.0,
                        "2020-01-01T02:00:00+00:00": 2.0,
                        "2020-01-01T03:00:00+00:00": 3.0,
                    }

            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                    "timezone": "Europe/Paris",
                },
                headers={"Accept": f"application/{format_}"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                if format_ == "csv":
                    ret_csv_lines = ret.data.decode("utf-8").splitlines()
                    assert ret_csv_lines[0] == ret_line_1
                    assert ret_csv_lines[1] == "2020-01-01T01:00:00+0100,0.0"
                else:
                    assert list(ret.json.keys()) == [str(ts_l[0])]
                    assert ret.json[str(ts_l[0])] == {
                        "2020-01-01T01:00:00+01:00": 0.0,
                        "2020-01-01T02:00:00+01:00": 1.0,
                        "2020-01-01T03:00:00+01:00": 2.0,
                        "2020-01-01T04:00:00+01:00": 3.0,
                    }

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
                headers={"Accept": f"application/{format_}"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 200
                if format_ == "csv":
                    ret_csv_lines = ret.data.decode("utf-8").splitlines()
                    assert ret_csv_lines[0] == ret_line_1
                    assert len(ret_csv_lines) > 1
                else:
                    assert list(ret.json.keys()) == [str(ts_l[0])]

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
                headers={"Accept": f"application/{format_}"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 422

            # Unknown format
            ret = client.get(
                query_url,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": ts_l,
                    "data_state": ds_id,
                },
                headers={"Accept": "Dummy"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 406

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("for_campaign", (True, False))
    @pytest.mark.parametrize("format_", ("json", "csv"))
    def test_timeseries_data_get_aggregate(
        self,
        app,
        user,
        users,
        campaigns,
        timeseries,
        timeseries_data,
        for_campaign,
        format_,
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
                headers={"Accept": f"application/{format_}"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                if format_ == "csv":
                    ret_csv_lines = ret.data.decode("utf-8").splitlines()
                    assert ret_csv_lines[0] == ret_line_1
                    assert len(ret_csv_lines) > 1
                else:
                    assert list(ret.json.keys()) == [str(ts_l[0])]

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
                headers={"Accept": f"application/{format_}"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                if format_ == "csv":
                    ret_csv_lines = ret.data.decode("utf-8").splitlines()
                    assert ret_csv_lines[0] == ret_line_1
                    assert len(ret_csv_lines) > 1
                else:
                    assert list(ret.json.keys()) == [str(ts_l[0])]

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
                headers={"Accept": f"application/{format_}"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 200
                if format_ == "csv":
                    ret_csv_lines = ret.data.decode("utf-8").splitlines()
                    assert ret_csv_lines[0] == ret_line_1
                    assert len(ret_csv_lines) > 1
                else:
                    assert list(ret.json.keys()) == [str(ts_l[0])]

            # Unknown format
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
                headers={"Accept": "Dummy"},
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 406

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

    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("for_campaign", (True, False))
    @pytest.mark.parametrize("format_", ("json", "csv"))
    def test_timeseries_data_post(
        self, app, user, users, campaigns, timeseries, for_campaign, format_
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

            if format_ == "csv":
                kwargs = {
                    "data": header
                    + (
                        "2020-01-01T00:00:00+00:00,0\n"
                        "2020-01-01T01:00:00+00:00,1\n"
                        "2020-01-01T02:00:00+00:00,2\n"
                        "2020-01-01T03:00:00+00:00,3\n"
                    )
                }
            else:
                kwargs = {
                    "json": {
                        str(ts_l[0]): {
                            "2020-01-01T00:00:00+00:00": 0,
                            "2020-01-01T01:00:00+00:00": 1,
                            "2020-01-01T02:00:00+00:00": 2,
                            "2020-01-01T03:00:00+00:00": 3,
                        }
                    }
                }
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                **kwargs,
                headers={"Accept": f"application/{format_}"},
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
                assert ret.json

            # User not in Timeseries group
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                header = f"Datetime,{ts_2_id}\n"
                ts_l = (ts_2_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_2_id}/"
                header = f"Datetime,Timeseries {ts_2_id-1}\n"
                ts_l = (f"Timeseries {ts_2_id-1}",)

            if format_ == "csv":
                kwargs = {
                    "data": header
                    + (
                        "2020-01-01T00:00:00+00:00,0\n"
                        "2020-01-01T01:00:00+00:00,1\n"
                        "2020-01-01T02:00:00+00:00,2\n"
                        "2020-01-01T03:00:00+00:00,3\n"
                    )
                }
            else:
                kwargs = {
                    "json": {
                        str(ts_l[0]): {
                            "2020-01-01T00:00:00+00:00": 0,
                            "2020-01-01T01:00:00+00:00": 1,
                            "2020-01-01T02:00:00+00:00": 2,
                            "2020-01-01T03:00:00+00:00": 3,
                        }
                    }
                }
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                **kwargs,
                headers={"Accept": f"application/{format_}"},
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
                assert ret.json

    @pytest.mark.parametrize("for_campaign", (True, False))
    @pytest.mark.parametrize("format_", ("json", "csv"))
    def test_timeseries_data_post_errors(
        self, app, users, campaigns, timeseries, for_campaign, format_
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
                ts_l = (f"Timeseries {ts_1_id-1}",)
                if format_ == "csv":
                    kwargs = {"data": header + "2020-01-01T00:00:00+00:00,0\n"}
                else:
                    kwargs = {"json": {str(ts_l[0]): {"2020-01-01T00:00:00+00:00": 0}}}
                ret = client.post(
                    query_url,
                    query_string={
                        "data_state": ds_id,
                    },
                    **kwargs,
                    headers={"Accept": f"application/{format_}"},
                )
                assert ret.status_code == 404

            # Unknown data state
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                header = f"Datetime,{ts_1_id}\n"
                ts_l = (ts_1_id,)
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
                header = f"Datetime,Timeseries {ts_1_id-1}\n"
                ts_l = (f"Timeseries {ts_1_id-1}",)
            if format_ == "csv":
                kwargs = {"data": header + "2020-01-01T00:00:00+00:00,0\n"}
            else:
                kwargs = {"json": {str(ts_l[0]): {"2020-01-01T00:00:00+00:00": 0}}}
            ret = client.post(
                query_url,
                query_string={
                    "data_state": DUMMY_ID,
                },
                **kwargs,
                headers={"Accept": f"application/{format_}"},
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

            if format_ == "csv":
                kwargs = {"data": header + "2020-01-01T00:00:00+00:00,0\n"}
            else:
                kwargs = {"json": {dummy_ts: {"2020-01-01T00:00:00+00:00": 0}}}
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                **kwargs,
                headers={"Accept": f"application/{format_}"},
            )
            assert ret.status_code == 422
            assert ret.json["message"].startswith("Unknown timeseries")

            # Invalid content
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
            else:
                query_url = TIMESERIES_DATA_URL + f"campaign/{campaign_1_id}/"
            if format_ == "csv":
                kwargs = {"data": ""}
            else:
                kwargs = {"json": {"dummy": []}}

            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                **kwargs,
                headers={"Accept": f"application/{format_}"},
            )
            assert ret.status_code == 422

            # Invalid TS IDs
            if not for_campaign:
                query_url = TIMESERIES_DATA_URL
                if format_ == "csv":
                    kwargs = {
                        "data": "Datetime,Timeseries 1\n2020-01-01T00:00:00+00:00,0\n"
                    }
                else:
                    kwargs = {
                        "json": {"Timeseries 1": {"2020-01-01T00:00:00+00:00": 0}}
                    }

                ret = client.post(
                    query_url,
                    query_string={
                        "data_state": ds_id,
                    },
                    **kwargs,
                    headers={"Accept": f"application/{format_}"},
                )
                assert ret.status_code == 422

            # Unknown format
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                **kwargs,
                headers={"Accept": "Dummy"},
            )
            assert ret.status_code == 406

            # Invalid payload
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                data=bytes.fromhex("2Ef0"),
                headers={"Accept": f"application/{format_}"},
            )
            assert ret.status_code == 422

            # Wrong format
            if format_ == "csv":
                kwargs = {"data": header + "2020-01-01T00:00:00+00:00,0\n"}
            else:
                kwargs = {"json": {str(ts_l[0]): {"2020-01-01T00:00:00+00:00": 0}}}
            wrong_format_ = {"json": "csv", "csv": "json"}[format_]
            ret = client.post(
                query_url,
                query_string={
                    "data_state": ds_id,
                },
                **kwargs,
                headers={"Accept": f"application/{wrong_format_}"},
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
                assert ret.json

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
                assert not ret.json

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
                assert ret.json

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
                assert not ret.json

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
