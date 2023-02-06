"""Timeseries by storeys routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_BY_STOREYS_URL = "/timeseries_by_storeys/"
STOREYS_URL = "/storeys/"


class TestTimeseriesByStoreyApi:
    def test_timeseries_by_storeys_api(self, app, users, storeys, timeseries):
        creds = users["Chuck"]["creds"]
        storey_1_id = storeys[0]
        storey_2_id = storeys[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(TIMESERIES_BY_STOREYS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tbs_1 = {
                "storey_id": storey_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_STOREYS_URL, json=tbs_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tbs_1_id = ret_val.pop("id")
            assert ret_val.pop("site")["name"] == "Site 1"
            assert ret_val.pop("building")["name"] == "Building 1"
            assert ret_val.pop("storey")["name"] == "Storey 1"
            assert ret_val == tbs_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_BY_STOREYS_URL, json=tbs_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_BY_STOREYS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_STOREYS_URL}{tbs_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val.pop("site")["name"] == "Site 1"
            assert ret_val.pop("building")["name"] == "Building 1"
            assert ret_val.pop("storey")["name"] == "Storey 1"
            assert ret_val == tbs_1

            # POST sep 2
            tbs_2 = {
                "storey_id": storey_2_id,
                "timeseries_id": ts_2_id,
            }
            ret = client.post(TIMESERIES_BY_STOREYS_URL, json=tbs_2)
            ret_val = ret.json
            tbs_2_id = ret_val.pop("id")

            # GET list
            ret = client.get(TIMESERIES_BY_STOREYS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                TIMESERIES_BY_STOREYS_URL,
                query_string={"storey_id": storey_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbs_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{TIMESERIES_BY_STOREYS_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE storey cascade
            ret = client.get(f"{STOREYS_URL}{storey_1_id}")
            storey_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{STOREYS_URL}{storey_1_id}", headers={"If-Match": storey_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(f"{TIMESERIES_BY_STOREYS_URL}{tbs_1_id}")
            assert ret.status_code == 404
            ret = client.delete(f"{TIMESERIES_BY_STOREYS_URL}{tbs_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_BY_STOREYS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_BY_STOREYS_URL}{tbs_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_timeseries_by_storeys_as_user_api(
        self, app, users, storeys, timeseries, timeseries_by_storeys
    ):
        user_creds = users["Active"]["creds"]
        storey_1_id = storeys[0]
        ts_1_id = timeseries[0]
        tbs_1_id = timeseries_by_storeys[0]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(TIMESERIES_BY_STOREYS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            tbs_1 = ret_val[0]
            assert tbs_1.pop("id") == tbs_1_id

            # POST
            tbs_3 = {
                "storey_id": storey_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_STOREYS_URL, json=tbs_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_STOREYS_URL}{tbs_1_id}")
            assert ret.status_code == 200

            # DELETE
            ret = client.delete(f"{TIMESERIES_BY_STOREYS_URL}{tbs_1_id}")
            assert ret.status_code == 403

    def test_timeseries_by_storeys_as_anonym_api(
        self, app, storeys, timeseries, timeseries_by_storeys
    ):
        storey_1_id = storeys[0]
        ts_2_id = timeseries[1]
        tbs_1_id = timeseries_by_storeys[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_BY_STOREYS_URL)
        assert ret.status_code == 401

        # POST
        tbs_3 = {
            "storey_id": storey_1_id,
            "timeseries_id": ts_2_id,
        }
        ret = client.post(TIMESERIES_BY_STOREYS_URL, json=tbs_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_BY_STOREYS_URL}{tbs_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{TIMESERIES_BY_STOREYS_URL}{tbs_1_id}")
        assert ret.status_code == 401
