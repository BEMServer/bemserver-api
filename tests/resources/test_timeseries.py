"""Timeseries tests"""
import contextlib

import pytest

from tests.common import AuthTestConfig, AuthHeader


DUMMY_ID = '69'

TIMESERIES_URL = '/timeseries/'
CAMPAIGNS_URL = '/campaigns/'


class TestTimeseriesApi:

    def test_timeseries_api(self, app):

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # POST
        timeseries_1 = {
            'name': 'Timeseries 1',
            'description': 'Timeseries example 1'
        }
        ret = client.post(TIMESERIES_URL, json=timeseries_1)
        assert ret.status_code == 201
        ret_val = ret.json
        timeseries_1_id = ret_val.pop('id')
        timeseries_1_etag = ret.headers['ETag']
        assert ret_val == timeseries_1

        # POST violating unique constraint
        ret = client.post(TIMESERIES_URL, json=timeseries_1)
        assert ret.status_code == 409

        # GET list
        ret = client.get(TIMESERIES_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]['id'] == timeseries_1_id

        # GET by id
        ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
        assert ret.status_code == 200
        assert ret.headers['ETag'] == timeseries_1_etag
        ret_val = ret.json
        ret_val.pop('id')
        assert ret_val == timeseries_1

        # PUT
        del timeseries_1['description']
        ret = client.put(
            f"{TIMESERIES_URL}{timeseries_1_id}",
            json=timeseries_1,
            headers={'If-Match': timeseries_1_etag}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        ret_val.pop('id')
        timeseries_1_etag = ret.headers['ETag']
        assert ret_val == timeseries_1

        # PUT wrong ID -> 404
        ret = client.put(
            f"{TIMESERIES_URL}{DUMMY_ID}",
            json=timeseries_1,
            headers={'If-Match': timeseries_1_etag}
        )
        assert ret.status_code == 404

        # POST TS 2
        timeseries_2 = {
            'name': 'Timeseries 2',
        }
        ret = client.post(TIMESERIES_URL, json=timeseries_2)
        ret_val = ret.json
        timeseries_2_id = ret_val.pop('id')
        timeseries_2_etag = ret.headers['ETag']

        # PUT violating unique constraint
        timeseries_2['name'] = timeseries_1['name']
        ret = client.put(
            f"{TIMESERIES_URL}{timeseries_2_id}",
            json=timeseries_2,
            headers={'If-Match': timeseries_2_etag}
        )
        assert ret.status_code == 409

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_URL}{timeseries_1_id}",
            headers={'If-Match': timeseries_1_etag}
        )
        assert ret.status_code == 204
        ret = client.delete(
            f"{TIMESERIES_URL}{timeseries_2_id}",
            headers={'If-Match': timeseries_2_etag}
        )

        # GET list
        ret = client.get(TIMESERIES_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # GET by id -> 404
        ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
        assert ret.status_code == 404

    @pytest.mark.parametrize(
        "app", (AuthTestConfig, ), indirect=True
    )
    def test_timeseries_as_admin_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200

            # POST
            timeseries_1 = {
                'name': 'Timeseries 1',
                'description': 'Timeseries example 1'
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == 201
            timeseries_1_id = ret.json['id']
            timeseries_1_etag = ret.headers['ETag']

            # GET by id
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == 200

            # PUT
            del timeseries_1['description']
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                json=timeseries_1,
                headers={'If-Match': timeseries_1_etag}
            )
            assert ret.status_code == 200
            timeseries_1_etag = ret.headers['ETag']

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                headers={'If-Match': timeseries_1_etag}
            )
            assert ret.status_code == 204

    @pytest.mark.parametrize(
        "app", (AuthTestConfig, ), indirect=True
    )
    @pytest.mark.parametrize("user", ("user", "anonym"))
    def test_timeseries_as_user_or_anonym_api(
        self, app, user, users, timeseries_data
    ):

        timeseries_1_id = timeseries_data[0][0]

        if user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
            status_code = 403
        else:
            auth_context = contextlib.nullcontext()
            status_code = 401

        client = app.test_client()

        with auth_context:

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == status_code

            # POST
            timeseries_1 = {
                'name': 'Timeseries 1',
                'description': 'Timeseries example 1'
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == status_code

            # GET by id
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == status_code

            # PUT
            del timeseries_1['description']
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                json=timeseries_1,
                headers={'If-Match': "Dummy-ETag"}
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == status_code

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                headers={'If-Match': "Dummy-ETag"}
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == status_code


class TestTimeseriesForCampaignApi:

    @pytest.mark.parametrize(
        "app", (AuthTestConfig, ), indirect=True
    )
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("timeseries_by_campaigns")
    @pytest.mark.usefixtures("users_by_campaigns")
    def test_timeseries_for_campaign_api(
        self, app, user, users, campaigns, timeseries_data
    ):
        campaign_1_id, _ = campaigns
        timeseries_1_id = timeseries_data[0][0]

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

            # GET list
            ret = client.get(f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries/")
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                ret_val = ret.json
                assert len(ret_val) == 1
                assert ret_val[0]["id"] == timeseries_1_id

            # GET by id
            ret = client.get(
                f"{CAMPAIGNS_URL}{campaign_1_id}/timeseries/{timeseries_1_id}")
            if user == "anonym":
                assert ret.status_code == 401
            else:
                assert ret.status_code == 200
                assert ret.json["id"] == timeseries_1_id
