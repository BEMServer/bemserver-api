"""Timeseries by spaces routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_BY_SPACES_URL = "/timeseries_by_spaces/"
SPACES_URL = "/spaces/"


class TestTimeseriesBySpaceApi:
    def test_timeseries_by_spaces_api(self, app, users, spaces, timeseries):
        creds = users["Chuck"]["creds"]
        space_1_id = spaces[0]
        space_2_id = spaces[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(TIMESERIES_BY_SPACES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tbs_1 = {
                "space_id": space_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_SPACES_URL, json=tbs_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tbs_1_id = ret_val.pop("id")
            assert ret_val.pop("site")["name"] == "Site 1"
            assert ret_val.pop("building")["name"] == "Building 1"
            assert ret_val.pop("storey")["name"] == "Storey 1"
            assert ret_val.pop("space")["name"] == "Space 1"
            assert ret_val == tbs_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_BY_SPACES_URL, json=tbs_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_BY_SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_SPACES_URL}{tbs_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val.pop("site")["name"] == "Site 1"
            assert ret_val.pop("building")["name"] == "Building 1"
            assert ret_val.pop("storey")["name"] == "Storey 1"
            assert ret_val.pop("space")["name"] == "Space 1"
            assert ret_val == tbs_1

            # POST sep 2
            tbs_2 = {
                "space_id": space_2_id,
                "timeseries_id": ts_2_id,
            }
            ret = client.post(TIMESERIES_BY_SPACES_URL, json=tbs_2)
            ret_val = ret.json
            tbs_2_id = ret_val.pop("id")

            # GET list
            ret = client.get(TIMESERIES_BY_SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                TIMESERIES_BY_SPACES_URL,
                query_string={"space_id": space_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbs_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{TIMESERIES_BY_SPACES_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE space cascade
            ret = client.get(f"{SPACES_URL}{space_1_id}")
            space_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{SPACES_URL}{space_1_id}", headers={"If-Match": space_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(f"{TIMESERIES_BY_SPACES_URL}{tbs_1_id}")
            assert ret.status_code == 404
            ret = client.delete(f"{TIMESERIES_BY_SPACES_URL}{tbs_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_BY_SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_BY_SPACES_URL}{tbs_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_timeseries_by_spaces_as_user_api(
        self, app, users, spaces, timeseries, timeseries_by_spaces
    ):
        user_creds = users["Active"]["creds"]
        space_1_id = spaces[0]
        ts_1_id = timeseries[0]
        tbs_1_id = timeseries_by_spaces[0]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(TIMESERIES_BY_SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            tbs_1 = ret_val[0]
            assert tbs_1.pop("id") == tbs_1_id

            # POST
            tbs_3 = {
                "space_id": space_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_SPACES_URL, json=tbs_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_SPACES_URL}{tbs_1_id}")
            assert ret.status_code == 200

            # DELETE
            ret = client.delete(f"{TIMESERIES_BY_SPACES_URL}{tbs_1_id}")
            assert ret.status_code == 403

    def test_timeseries_by_spaces_as_anonym_api(
        self, app, spaces, timeseries, timeseries_by_spaces
    ):
        space_1_id = spaces[0]
        ts_2_id = timeseries[1]
        tbs_1_id = timeseries_by_spaces[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_BY_SPACES_URL)
        assert ret.status_code == 401

        # POST
        tbs_3 = {
            "space_id": space_1_id,
            "timeseries_id": ts_2_id,
        }
        ret = client.post(TIMESERIES_BY_SPACES_URL, json=tbs_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_BY_SPACES_URL}{tbs_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{TIMESERIES_BY_SPACES_URL}{tbs_1_id}")
        assert ret.status_code == 401
