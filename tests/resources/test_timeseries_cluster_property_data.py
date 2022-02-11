"""Timeseries cluster property data tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_CLUSTER_PROPERTY_DATA_URL = "/timeseries_cluster_property_data/"


class TestTimeseriesClusterPropertyDataApi:
    def test_timeseries_cluster_property_data_api(
        self, app, users, timeseries_properties, timeseries_clusters
    ):

        tsp_1_id = timeseries_properties[0]
        tsp_2_id = timeseries_properties[1]
        tsc_1_id = timeseries_clusters[0]

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_CLUSTER_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tscg_1 = {
                "cluster_id": tsc_1_id,
                "property_id": tsp_1_id,
                "value": 12,
            }
            ret = client.post(TIMESERIES_CLUSTER_PROPERTY_DATA_URL, json=tscg_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tscg_1_id = ret_val.pop("id")
            tscg_1_etag = ret.headers["ETag"]
            assert ret_val == tscg_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_CLUSTER_PROPERTY_DATA_URL, json=tscg_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_CLUSTER_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tscg_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscg_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tscg_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tscg_1

            # PUT
            tscg_1["value"] = 42
            ret = client.put(
                f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscg_1_id}",
                json=tscg_1,
                headers={"If-Match": tscg_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tscg_1_etag = ret.headers["ETag"]
            assert ret_val == tscg_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{DUMMY_ID}",
                json=tscg_1,
                headers={"If-Match": tscg_1_etag},
            )
            assert ret.status_code == 404

            # POST TSPD 2
            tscg_2 = {
                "cluster_id": tsc_1_id,
                "property_id": tsp_2_id,
                "value": 42,
            }
            ret = client.post(TIMESERIES_CLUSTER_PROPERTY_DATA_URL, json=tscg_2)
            ret_val = ret.json
            tscg_2_id = ret_val.pop("id")
            tscg_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tscg_2["property_id"] = tsp_1_id
            ret = client.put(
                f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscg_2_id}",
                json=tscg_2,
                headers={"If-Match": tscg_2_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscg_1_id}",
                headers={"If-Match": tscg_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscg_2_id}",
                headers={"If-Match": tscg_2_etag},
            )

            # GET list
            ret = client.get(TIMESERIES_CLUSTER_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscg_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("timeseries_cluster_groups_by_users")
    def test_timeseries_cluster_property_data_as_user_api(
        self,
        app,
        users,
        timeseries_properties,
        timeseries_clusters,
        timeseries_cluster_property_data,
    ):

        tsp_1_id = timeseries_properties[0]
        tsc_1_id = timeseries_clusters[0]
        tscpd_1_id = timeseries_cluster_property_data[0]
        tscpd_3_id = timeseries_cluster_property_data[2]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_CLUSTER_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert all([tscpd["cluster_id"] == tsc_1_id for tscpd in ret_val])

            # POST
            tscpd = {
                "cluster_id": tsc_1_id,
                "property_id": tsp_1_id,
                "value": 12,
            }
            ret = client.post(TIMESERIES_CLUSTER_PROPERTY_DATA_URL, json=tscpd)
            # This would trigger a unique constraint violation error
            # but we get rejected before that
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscpd_1_id}")
            assert ret.status_code == 200
            ts_1_etag = ret.headers["ETag"]
            ret_val = ret.json
            ret_val.pop("id")
            tscpd_1 = ret_val

            # GET by id, user not in group
            ret = client.get(f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscpd_3_id}")
            assert ret.status_code == 403

            # PUT
            tscpd_1["value"] = 42
            ret = client.put(
                f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscpd_1_id}",
                json=tscpd_1,
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscpd_1_id}",
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

    def test_timeseries_cluster_property_data_as_anonym_api(
        self,
        app,
        users,
        timeseries_properties,
        timeseries_clusters,
        timeseries_cluster_property_data,
    ):

        tsp_1_id = timeseries_properties[0]
        tsc_1_id = timeseries_clusters[0]
        tscpd_1_id = timeseries_cluster_property_data[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_CLUSTER_PROPERTY_DATA_URL)
        assert ret.status_code == 401

        # POST
        tscpd = {
            "cluster_id": tsc_1_id,
            "property_id": tsp_1_id,
            "value": 12,
        }
        ret = client.post(TIMESERIES_CLUSTER_PROPERTY_DATA_URL, json=tscpd)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscpd_1_id}")
        assert ret.status_code == 401

        # PUT
        tscpd["value"] = 42
        ret = client.put(
            f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscpd_1_id}",
            json=tscpd,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_CLUSTER_PROPERTY_DATA_URL}{tscpd_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
