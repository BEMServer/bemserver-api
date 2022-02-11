"""Timeseries data states tests"""
from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_DATA_STATES_URL = "/timeseries_data_states/"


class TestTimeseriesDataStatesApi:
    def test_timeseries_data_states_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_DATA_STATES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert {x["name"] for x in ret_val} == {"Raw", "Clean"}

            # POST
            tds_1 = {
                "name": "Quality",
            }
            ret = client.post(TIMESERIES_DATA_STATES_URL, json=tds_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tds_1_id = ret_val.pop("id")
            tds_1_etag = ret.headers["ETag"]
            assert ret_val == tds_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_DATA_STATES_URL, json=tds_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_DATA_STATES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 3
            assert {x["name"] for x in ret_val} == {"Raw", "Clean", "Quality"}

            # GET by id
            ret = client.get(f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tds_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tds_1

            # PUT
            tds_1["name"] = "Qualität"
            ret = client.put(
                f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}",
                json=tds_1,
                headers={"If-Match": tds_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tds_1_etag = ret.headers["ETag"]
            assert ret_val == tds_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_DATA_STATES_URL}{DUMMY_ID}",
                json=tds_1,
                headers={"If-Match": tds_1_etag},
            )
            assert ret.status_code == 404

            # POST TSDS 2
            tds_2 = {
                "name": "Accuracy",
            }
            ret = client.post(TIMESERIES_DATA_STATES_URL, json=tds_2)
            ret_val = ret.json
            tds_2_id = ret_val.pop("id")
            tds_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tds_2["name"] = "Qualität"
            ret = client.put(
                f"{TIMESERIES_DATA_STATES_URL}{tds_2_id}",
                json=tds_2,
                headers={"If-Match": tds_2_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}",
                headers={"If-Match": tds_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_DATA_STATES_URL}{tds_2_id}",
                headers={"If-Match": tds_2_etag},
            )

            # GET list
            ret = client.get(TIMESERIES_DATA_STATES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert {x["name"] for x in ret_val} == {"Raw", "Clean"}

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}")
            assert ret.status_code == 404

    def test_timeseries_data_states_as_user_api(self, app, users, timeseries):

        tds_1_id = 1

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_DATA_STATES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert {x["name"] for x in ret_val} == {"Raw", "Clean"}

            # POST
            tds = {
                "name": "Quality",
            }
            ret = client.post(TIMESERIES_DATA_STATES_URL, json=tds)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}")
            assert ret.status_code == 200
            tds_1_etag = ret.headers["ETag"]
            ret_val = ret.json
            ret_val.pop("id")
            tds_1 = ret_val

            # PUT
            tds_1["name"] = "Qualität"
            ret = client.put(
                f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}",
                json=tds_1,
                headers={"If-Match": tds_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}",
                headers={"If-Match": tds_1_etag},
            )
            assert ret.status_code == 403

    def test_timeseries_data_states_as_anonym_api(self, app, users):

        tds_1_id = 1

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_DATA_STATES_URL)
        assert ret.status_code == 401

        # POST
        tds = {
            "name": "Quality",
        }
        ret = client.post(TIMESERIES_DATA_STATES_URL, json=tds)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}",
            json=tds,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_DATA_STATES_URL}{tds_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
