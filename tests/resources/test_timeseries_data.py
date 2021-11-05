"""Timeseries data tests"""
import contextlib
import io
import datetime as dt

import pytest

from tests.common import AuthHeader

TIMESERIES_DATA_URL = '/timeseries-data/'
CAMPAIGNS_URL = '/campaigns/'


class TestTimeseriesDataApi:

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 4}, ),
            indirect=True
    )
    def test_timeseries_data_get(self, app, users, timeseries_data):

        ts_0_id, _, start_time, end_time = timeseries_data[0]
        ts_1_id, _, _, _ = timeseries_data[1]

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            ret = client.get(
                TIMESERIES_DATA_URL,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ts_1_id],
                }
            )
            assert ret.status_code == 200
            assert ret.headers['Content-Type'] == "text/csv; charset=utf-8"
            assert ret.headers['Content-Disposition'] == (
                "attachment; filename=timeseries.csv"
            )
            csv_str = ret.data.decode("utf-8")
            assert csv_str == (
                f"Datetime,{ts_0_id},{ts_1_id}\n"
                "2020-01-01T00:00:00+0000,0.0,0.0\n"
                "2020-01-01T01:00:00+0000,1.0,1.0\n"
                "2020-01-01T02:00:00+0000,2.0,2.0\n"
                "2020-01-01T03:00:00+0000,3.0,3.0\n"
            )

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 4}, ),
            indirect=True
    )
    @pytest.mark.parametrize("user", ("user", "anonym"))
    def test_timeseries_data_get_as_user_or_anonym(
        self, app, user, users, timeseries_data
    ):

        ts_0_id, _, start_time, end_time = timeseries_data[0]
        ts_1_id, _, _, _ = timeseries_data[1]

        if user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
            status_code = 403
        else:
            auth_context = contextlib.nullcontext()
            status_code = 401

        client = app.test_client()

        with auth_context:

            ret = client.get(
                TIMESERIES_DATA_URL,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ts_1_id],
                }
            )
            assert ret.status_code == status_code

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 48}, ),
            indirect=True
    )
    def test_timeseries_data_get_aggregate(self, app, users, timeseries_data):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            ts_0_id, _, start_time, end_time = timeseries_data[0]
            ts_1_id, _, _, _ = timeseries_data[1]

            # UTC timezone, avg
            ret = client.get(
                TIMESERIES_DATA_URL + "aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ts_1_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                }
            )
            assert ret.status_code == 200
            assert ret.headers['Content-Type'] == "text/csv; charset=utf-8"
            assert ret.headers['Content-Disposition'] == (
                "attachment; filename=timeseries.csv"
            )
            csv_str = ret.data.decode("utf-8")
            assert csv_str == (
                f"Datetime,{ts_0_id},{ts_1_id}\n"
                "2020-01-01T00:00:00+0000,11.5,11.5\n"
                "2020-01-02T00:00:00+0000,35.5,35.5\n"
            )

            # Local timezone, avg
            ret = client.get(
                TIMESERIES_DATA_URL + "aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ts_1_id],
                    "bucket_width": "1 day",
                    "timezone": "Europe/Paris",
                }
            )
            assert ret.status_code == 200
            assert ret.headers['Content-Type'] == "text/csv; charset=utf-8"
            assert ret.headers['Content-Disposition'] == (
                "attachment; filename=timeseries.csv"
            )
            csv_str = ret.data.decode("utf-8")
            assert csv_str == (
                f"Datetime,{ts_0_id},{ts_1_id}\n"
                "2019-12-31T23:00:00+0000,11.0,11.0\n"
                "2020-01-01T23:00:00+0000,34.5,34.5\n"
                "2020-01-02T23:00:00+0000,47.0,47.0\n"
            )

            # UTC timezone, sum
            ret = client.get(
                TIMESERIES_DATA_URL + "aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ts_1_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                    "aggregation": "sum",
                }
            )
            assert ret.status_code == 200
            assert ret.headers['Content-Type'] == "text/csv; charset=utf-8"
            assert ret.headers['Content-Disposition'] == (
                "attachment; filename=timeseries.csv"
            )
            csv_str = ret.data.decode("utf-8")
            assert csv_str == (
                f"Datetime,{ts_0_id},{ts_1_id}\n"
                "2020-01-01T00:00:00+0000,276.0,276.0\n"
                "2020-01-02T00:00:00+0000,852.0,852.0\n"
            )

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 48}, ),
            indirect=True
    )
    @pytest.mark.parametrize("user", ("user", "anonym"))
    def test_timeseries_data_get_aggregate_as_user_or_anonym(
        self, app, user, users, timeseries_data
    ):

        ts_0_id, _, start_time, end_time = timeseries_data[0]
        ts_1_id, _, _, _ = timeseries_data[1]

        if user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
            status_code = 403
        else:
            auth_context = contextlib.nullcontext()
            status_code = 401

        client = app.test_client()

        with auth_context:

            # UTC timezone, avg
            ret = client.get(
                TIMESERIES_DATA_URL + "aggregate",
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ts_1_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                }
            )
            assert ret.status_code == status_code

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 0}, ),
            indirect=True
    )
    def test_timeseries_data_post(self, app, users, timeseries_data):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            start_time = dt.datetime(2020, 1, 1, 0, tzinfo=dt.timezone.utc)
            end_time = dt.datetime(2020, 1, 1, 4, tzinfo=dt.timezone.utc)

            ts_0_id, _, _, _ = timeseries_data[0]
            ts_1_id, _, _, _ = timeseries_data[1]

            # Check there is no data
            ret = client.get(
                TIMESERIES_DATA_URL,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ts_1_id],
                }
            )
            assert ret.status_code == 200
            assert ret.headers['Content-Type'] == "text/csv; charset=utf-8"
            assert ret.headers['Content-Disposition'] == (
                "attachment; filename=timeseries.csv"
            )
            csv_str = ret.data.decode("utf-8")
            assert csv_str == "Datetime,1,2\n"

            # Send data
            csv_str = (
                f"Datetime,{ts_0_id},{ts_1_id}\n"
                "2020-01-01T00:00:00+00:00,0,10\n"
                "2020-01-01T01:00:00+00:00,1,11\n"
                "2020-01-01T02:00:00+00:00,2,12\n"
                "2020-01-01T03:00:00+00:00,3,13\n"
            )

            ret = client.post(
                TIMESERIES_DATA_URL,
                data={
                    "csv_file": (
                        io.BytesIO(csv_str.encode()), 'timeseries.csv')
                }
            )
            assert ret.status_code == 201

            # Check data was written in DB
            ret = client.get(
                TIMESERIES_DATA_URL,
                query_string={
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ts_1_id],
                }
            )
            assert ret.status_code == 200
            assert ret.headers['Content-Type'] == "text/csv; charset=utf-8"
            assert ret.headers['Content-Disposition'] == (
                "attachment; filename=timeseries.csv"
            )
            csv_str = ret.data.decode("utf-8")
            assert csv_str == (
                f"Datetime,{ts_0_id},{ts_1_id}\n"
                "2020-01-01T00:00:00+0000,0.0,10.0\n"
                "2020-01-01T01:00:00+0000,1.0,11.0\n"
                "2020-01-01T02:00:00+0000,2.0,12.0\n"
                "2020-01-01T03:00:00+0000,3.0,13.0\n"
            )

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 1, "nb_tsd": 0}, ),
            indirect=True
    )
    @pytest.mark.parametrize(
        "csv_str",
        (
            "",
            "Dummy,\n",
            "Datetime,1324564",
            "Datetime,1\n2020-01-01T00:00:00+00:00",
            "Datetime,1\n2020-01-01T00:00:00+00:00,",
            "Datetime,1\n2020-01-01T00:00:00+00:00,a",
        )
    )
    @pytest.mark.usefixtures("timeseries_data")
    def test_timeseries_data_post_error(self, app, users, csv_str):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            ret = client.post(
                TIMESERIES_DATA_URL,
                data={
                    "csv_file": (
                        io.BytesIO(csv_str.encode()), 'timeseries.csv')
                }
            )
            assert ret.status_code == 422
            assert ret.json == {
                "code": 422,
                "status": "Unprocessable Entity",
            }

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 0}, ),
            indirect=True
    )
    @pytest.mark.parametrize("user", ("user", "anonym"))
    def test_timeseries_data_post_as_user_or_anonym(
        self, app, user, users, timeseries_data
    ):

        ts_0_id, _, _, _ = timeseries_data[0]
        ts_1_id, _, _, _ = timeseries_data[1]

        if user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
            status_code = 403
        else:
            auth_context = contextlib.nullcontext()
            status_code = 401

        client = app.test_client()

        with auth_context:

            csv_str = (
                f"Datetime,{ts_0_id},{ts_1_id}\n"
                "2020-01-01T00:00:00+00:00,0,10\n"
                "2020-01-01T01:00:00+00:00,1,11\n"
                "2020-01-01T02:00:00+00:00,2,12\n"
                "2020-01-01T03:00:00+00:00,3,13\n"
            )

            ret = client.post(
                TIMESERIES_DATA_URL,
                data={
                    "csv_file": (
                        io.BytesIO(csv_str.encode()),
                        'timeseries.csv'
                    )
                }
            )
            assert ret.status_code == status_code


class TestTimeseriesDataForCampaignApi:

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 4}, ),
            indirect=True
    )
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_campaigns")
    @pytest.mark.usefixtures("timeseries_by_campaigns")
    def test_timeseries_data_for_campaign_get(
        self, app, user, users, campaigns, timeseries_data,
    ):

        ts_0_id, _, start_time, end_time = timeseries_data[0]
        ts_1_id, _, _, _ = timeseries_data[1]
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
                    "timeseries": [ts_0_id, ],
                }
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
                    "timeseries": [ts_0_id, ],
                }
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
                    "timeseries": [ts_1_id, ],
                }
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
                    "start_time": (
                        start_time - dt.timedelta(days=1)
                    ).isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id, ],
                }
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 4}, ),
            indirect=True
    )
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_campaigns")
    @pytest.mark.usefixtures("timeseries_by_campaigns")
    def test_timeseries_data_for_campaign_get_aggregate(
        self, app, user, users, campaigns, timeseries_data,
    ):

        ts_0_id, _, start_time, end_time = timeseries_data[0]
        ts_1_id, _, _, _ = timeseries_data[1]
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
                    "timeseries": [ts_0_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                }
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
                    "timeseries": [ts_0_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                }
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
                    "timeseries": [ts_1_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                }
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
                    "start_time": (
                        start_time - dt.timedelta(days=1)
                    ).isoformat(),
                    "end_time": end_time.isoformat(),
                    "timeseries": [ts_0_id],
                    "bucket_width": "1 day",
                    "timezone": "UTC",
                }
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403

    @pytest.mark.parametrize(
            'timeseries_data',
            ({"nb_ts": 2, "nb_tsd": 0}, ),
            indirect=True
    )
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_campaigns")
    @pytest.mark.usefixtures("timeseries_by_campaigns")
    @pytest.mark.usefixtures("timeseries_by_campaigns_by_users")
    def test_timeseries_data_for_campaign_post(
            self, app, user, users, campaigns, timeseries_data
    ):

        ts_0_id, _, _, _ = timeseries_data[0]
        ts_1_id, _, _, _ = timeseries_data[1]
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
                f"Datetime,{ts_0_id}\n"
                "2020-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/",
                data={
                    "csv_file": (
                        io.BytesIO(csv_str.encode()), 'timeseries.csv')
                }
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 201

            # Timeseries not in Campaign
            csv_str = (
                f"Datetime,{ts_1_id}\n"
                "2020-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/",
                data={
                    "csv_file": (
                        io.BytesIO(csv_str.encode()), 'timeseries.csv')
                }
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403

            # User not in Campaign
            csv_str = (
                f"Datetime,{ts_1_id}\n"
                "2020-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                f"{CAMPAIGNS_URL}{campaign_2_id}/timeseries_data/",
                data={
                    "csv_file": (
                        io.BytesIO(csv_str.encode()), 'timeseries.csv')
                }
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 201

            # TODO: User not in Campaign x Timeseries

            # Time range exceeds Campaign
            csv_str = (
                f"Datetime,{ts_0_id}\n"
                "2019-01-01T00:00:00+00:00,0\n"
                "2020-01-01T01:00:00+00:00,1\n"
                "2020-01-01T02:00:00+00:00,2\n"
                "2020-01-01T03:00:00+00:00,3\n"
            )
            ret = client.post(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries_data/",
                data={
                    "csv_file": (
                        io.BytesIO(csv_str.encode()), 'timeseries.csv')
                }
            )
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 403
