"""Timeseries properties tests"""
import copy

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_PROPERTIES_URL = "/timeseries_properties/"


class TestTimeseriesDataStatesApi:
    def test_timeseries_properties_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            nb_ts_props = len(ret_val)
            assert nb_ts_props > 0
            nb_float = len([x for x in ret_val if x["value_type"] == "float"])
            nb_bool = len([x for x in ret_val if x["value_type"] == "boolean"])

            # POST
            tsp_1 = {
                "name": "Deutsche Qualität",
                "value_type": "float",
                "unit_symbol": "Qualität unit",
            }
            ret = client.post(TIMESERIES_PROPERTIES_URL, json=tsp_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tsp_1_id = ret_val.pop("id")
            tsp_1_etag = ret.headers["ETag"]
            assert ret_val == tsp_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_PROPERTIES_URL, json=tsp_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_ts_props + 1
            assert tsp_1["name"] in [x["name"] for x in ret_val]

            # GET by id
            ret = client.get(f"{TIMESERIES_PROPERTIES_URL}{tsp_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tsp_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tsp_1

            # PUT
            tsp_1["name"] = "Qualität"
            tsp_1_put = copy.deepcopy(tsp_1)
            del tsp_1_put["value_type"]
            ret = client.put(
                f"{TIMESERIES_PROPERTIES_URL}{tsp_1_id}",
                json=tsp_1_put,
                headers={"If-Match": tsp_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tsp_1_etag = ret.headers["ETag"]
            assert ret_val == tsp_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_PROPERTIES_URL}{DUMMY_ID}",
                json=tsp_1_put,
                headers={"If-Match": tsp_1_etag},
            )
            assert ret.status_code == 404

            # POST TSP 2
            tsp_2 = {
                "name": "Autentica qualità",
                "value_type": "float",
            }
            ret = client.post(TIMESERIES_PROPERTIES_URL, json=tsp_2)
            ret_val = ret.json
            tsp_2_id = ret_val.pop("id")
            tsp_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tsp_2_put = copy.deepcopy(tsp_2)
            del tsp_2_put["value_type"]
            tsp_2_put["name"] = "Qualität"
            ret = client.put(
                f"{TIMESERIES_PROPERTIES_URL}{tsp_2_id}",
                json=tsp_2_put,
                headers={"If-Match": tsp_2_etag},
            )
            assert ret.status_code == 409

            # GET list with filters
            ret = client.get(
                TIMESERIES_PROPERTIES_URL, query_string={"name": "Qualität"}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tsp_1_id
            ret = client.get(
                TIMESERIES_PROPERTIES_URL,
                query_string={"value_type": "float"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_float + 2
            ret = client.get(
                TIMESERIES_PROPERTIES_URL,
                query_string={"value_type": "boolean"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_bool
            ret = client.get(
                TIMESERIES_PROPERTIES_URL,
                query_string={"unit_symbol": "Qualität unit"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ret = client.get(
                TIMESERIES_PROPERTIES_URL,
                query_string={"unit_symbol": "Qualità unit"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_PROPERTIES_URL}{tsp_1_id}",
                headers={"If-Match": tsp_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_PROPERTIES_URL}{tsp_2_id}",
                headers={"If-Match": tsp_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_ts_props

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_PROPERTIES_URL}{tsp_1_id}")
            assert ret.status_code == 404

    def test_timeseries_properties_as_user_api(self, app, users):

        tds_1_id = 1

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            nb_ts_props = len(ret_val)
            assert nb_ts_props > 0

            # POST
            tds = {
                "name": "Frequency (test)",
                "value_type": "integer",
            }
            ret = client.post(TIMESERIES_PROPERTIES_URL, json=tds)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_PROPERTIES_URL}{tds_1_id}")
            assert ret.status_code == 200
            tds_1_etag = ret.headers["ETag"]
            ret_val = ret.json
            ret_val.pop("id")
            tds_1 = ret_val

            # PUT
            tds_1_put = copy.deepcopy(tds_1)
            del tds_1_put["value_type"]
            tds_1_put["name"] = "Qualität"
            ret = client.put(
                f"{TIMESERIES_PROPERTIES_URL}{tds_1_id}",
                json=tds_1_put,
                headers={"If-Match": tds_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_PROPERTIES_URL}{tds_1_id}",
                headers={"If-Match": tds_1_etag},
            )
            assert ret.status_code == 403

    def test_timeseries_properties_as_anonym_api(
        self, app, users, timeseries_properties
    ):

        tsp_1_id = timeseries_properties[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_PROPERTIES_URL)
        assert ret.status_code == 401

        # POST
        tds = {
            "name": "Frequency (test)",
        }
        ret = client.post(TIMESERIES_PROPERTIES_URL, json=tds)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_PROPERTIES_URL}{tsp_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{TIMESERIES_PROPERTIES_URL}{tsp_1_id}",
            json=tds,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_PROPERTIES_URL}{tsp_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
