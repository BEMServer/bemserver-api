"""Timeseries property data tests"""
import copy
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_PROPERTY_DATA_URL = "/timeseries_property_data/"


class TestTimeseriesPropertyDataApi:
    def test_timeseries_property_data_api(
        self, app, users, timeseries_properties, timeseries
    ):

        tsp_1_id = timeseries_properties[0]
        tsp_2_id = timeseries_properties[1]
        ts_1_id = timeseries[0]

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tsg_1 = {
                "timeseries_id": ts_1_id,
                "property_id": tsp_1_id,
                "value": "12",
            }
            ret = client.post(TIMESERIES_PROPERTY_DATA_URL, json=tsg_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tsg_1_id = ret_val.pop("id")
            tsg_1_etag = ret.headers["ETag"]
            assert ret_val == tsg_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_PROPERTY_DATA_URL, json=tsg_1)
            assert ret.status_code == 409

            # POST wrong value type
            tsg_post = {
                "timeseries_id": ts_1_id,
                "property_id": tsp_2_id,
                "value": "wrong type",
            }
            ret = client.post(TIMESERIES_PROPERTY_DATA_URL, json=tsg_post)
            assert ret.status_code == 422

            # GET list
            ret = client.get(TIMESERIES_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tsg_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_PROPERTY_DATA_URL}{tsg_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tsg_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tsg_1

            # PUT
            tsg_1["value"] = "42"
            ret = client.put(
                f"{TIMESERIES_PROPERTY_DATA_URL}{tsg_1_id}",
                json=tsg_1,
                headers={"If-Match": tsg_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tsg_1_etag = ret.headers["ETag"]
            assert ret_val == tsg_1

            # PUT wrong value type
            tsg_1_put = copy.deepcopy(tsg_1)
            tsg_1_put["value"] = "wrong type"
            ret = client.put(
                f"{TIMESERIES_PROPERTY_DATA_URL}{tsg_1_id}",
                json=tsg_1_put,
                headers={"If-Match": tsg_1_etag},
            )
            assert ret.status_code == 422

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_PROPERTY_DATA_URL}{DUMMY_ID}",
                json=tsg_1,
                headers={"If-Match": tsg_1_etag},
            )
            assert ret.status_code == 404

            # POST TSPD 2
            tsg_2 = {
                "timeseries_id": ts_1_id,
                "property_id": tsp_2_id,
                "value": "42",
            }
            ret = client.post(TIMESERIES_PROPERTY_DATA_URL, json=tsg_2)
            ret_val = ret.json
            tsg_2_id = ret_val.pop("id")
            tsg_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tsg_2["property_id"] = tsp_1_id
            ret = client.put(
                f"{TIMESERIES_PROPERTY_DATA_URL}{tsg_2_id}",
                json=tsg_2,
                headers={"If-Match": tsg_2_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_PROPERTY_DATA_URL}{tsg_1_id}",
                headers={"If-Match": tsg_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_PROPERTY_DATA_URL}{tsg_2_id}",
                headers={"If-Match": tsg_2_etag},
            )

            # GET list
            ret = client.get(TIMESERIES_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_PROPERTY_DATA_URL}{tsg_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_timeseries_property_data_as_user_api(
        self,
        app,
        users,
        timeseries_properties,
        timeseries,
        timeseries_property_data,
    ):

        tsp_1_id = timeseries_properties[0]
        ts_1_id = timeseries[0]
        tspd_1_id = timeseries_property_data[0]
        tspd_3_id = timeseries_property_data[2]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert all([tspd["timeseries_id"] == ts_1_id for tspd in ret_val])

            # POST
            tspd = {
                "timeseries_id": ts_1_id,
                "property_id": tsp_1_id,
                "value": "12",
            }
            ret = client.post(TIMESERIES_PROPERTY_DATA_URL, json=tspd)
            # This would trigger a unique constraint violation error
            # but we get rejected before that
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_PROPERTY_DATA_URL}{tspd_1_id}")
            assert ret.status_code == 200
            ts_1_etag = ret.headers["ETag"]
            ret_val = ret.json
            ret_val.pop("id")
            tspd_1 = ret_val

            # GET by id, user not in group
            ret = client.get(f"{TIMESERIES_PROPERTY_DATA_URL}{tspd_3_id}")
            assert ret.status_code == 403

            # PUT
            tspd_1["value"] = "42"
            ret = client.put(
                f"{TIMESERIES_PROPERTY_DATA_URL}{tspd_1_id}",
                json=tspd_1,
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_PROPERTY_DATA_URL}{tspd_1_id}",
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

    def test_timeseries_property_data_as_anonym_api(
        self,
        app,
        users,
        timeseries_properties,
        timeseries,
        timeseries_property_data,
    ):

        tsp_1_id = timeseries_properties[0]
        ts_1_id = timeseries[0]
        tspd_1_id = timeseries_property_data[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_PROPERTY_DATA_URL)
        assert ret.status_code == 401

        # POST
        tspd = {
            "timeseries_id": ts_1_id,
            "property_id": tsp_1_id,
            "value": "12",
        }
        ret = client.post(TIMESERIES_PROPERTY_DATA_URL, json=tspd)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_PROPERTY_DATA_URL}{tspd_1_id}")
        assert ret.status_code == 401

        # PUT
        tspd["value"] = "42"
        ret = client.put(
            f"{TIMESERIES_PROPERTY_DATA_URL}{tspd_1_id}",
            json=tspd,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_PROPERTY_DATA_URL}{tspd_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
