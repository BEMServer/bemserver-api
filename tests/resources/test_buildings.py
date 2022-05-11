"""Buildings routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

BUILDINGS_URL = "/buildings/"


class TestBuildingsApi:
    def test_buildings_api(self, app, users, campaigns, sites):

        creds = users["Chuck"]["creds"]
        campaign_2_id = campaigns[1]
        site_1_id = sites[0]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(BUILDINGS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            building_1 = {
                "name": "Building 1",
                "site_id": site_1_id,
            }
            ret = client.post(BUILDINGS_URL, json=building_1)
            assert ret.status_code == 201
            ret_val = ret.json
            building_1_id = ret_val.pop("id")
            building_1_etag = ret.headers["ETag"]
            assert ret_val == building_1

            # POST violating unique constraint
            ret = client.post(BUILDINGS_URL, json=building_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == building_1_id

            # GET by id
            ret = client.get(f"{BUILDINGS_URL}{building_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == building_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == building_1

            # PUT
            building_1["description"] = "Fantastic building"
            building_1_put = building_1.copy()
            del building_1_put["site_id"]
            ret = client.put(
                f"{BUILDINGS_URL}{building_1_id}",
                json=building_1_put,
                headers={"If-Match": building_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            building_1_etag = ret.headers["ETag"]
            assert ret_val == building_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{BUILDINGS_URL}{DUMMY_ID}",
                json=building_1_put,
                headers={"If-Match": building_1_etag},
            )
            assert ret.status_code == 404

            # POST building 2
            building_2 = {
                "name": "Building 2",
                "site_id": site_1_id,
            }
            ret = client.post(BUILDINGS_URL, json=building_2)
            ret_val = ret.json
            building_2_id = ret_val.pop("id")
            building_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            building_1_put["name"] = building_2["name"]
            ret = client.put(
                f"{BUILDINGS_URL}{building_1_id}",
                json=building_1_put,
                headers={"If-Match": building_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(BUILDINGS_URL, query_string={"name": "Building 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == building_1_id
            ret = client.get(BUILDINGS_URL, query_string={"campaign_id": campaign_2_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{BUILDINGS_URL}{DUMMY_ID}", headers={"If-Match": building_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{BUILDINGS_URL}{building_1_id}", headers={"If-Match": building_1_etag}
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{BUILDINGS_URL}{building_2_id}", headers={"If-Match": building_2_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{BUILDINGS_URL}{building_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_buildings_as_user_api(self, app, users, sites, buildings):

        user_creds = users["Active"]["creds"]
        site_2_id = sites[1]
        building_1_id = buildings[0]
        building_2_id = buildings[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(BUILDINGS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            building_1 = ret_val[0]
            assert building_1.pop("id") == building_1_id

            # GET list with filters
            ret = client.get(BUILDINGS_URL, query_string={"name": "Building 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == building_1_id
            ret = client.get(BUILDINGS_URL, query_string={"name": "Building 2"})
            assert ret.status_code == 200
            assert not ret.json

            # POST
            building_3 = {
                "name": "Building 3",
                "site_id": site_2_id,
            }
            ret = client.post(BUILDINGS_URL, json=building_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{BUILDINGS_URL}{building_1_id}")
            assert ret.status_code == 200
            building_1_etag = ret.headers["ETag"]

            ret = client.get(f"{BUILDINGS_URL}{building_2_id}")
            assert ret.status_code == 403

            # PUT
            building_1["description"] = "Fantastic building"
            building_1_put = building_1.copy()
            del building_1_put["site_id"]
            ret = client.put(
                f"{BUILDINGS_URL}{building_1_id}",
                json=building_1_put,
                headers={"If-Match": building_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{BUILDINGS_URL}{building_1_id}", headers={"If-Match": building_1_etag}
            )
            assert ret.status_code == 403

    def test_buildings_as_anonym_api(self, app, buildings, sites):

        building_1_id = buildings[0]
        site_1_id = sites[0]

        client = app.test_client()

        # GET list
        ret = client.get(BUILDINGS_URL)
        assert ret.status_code == 401

        # POST
        building_3 = {
            "name": "Building 3",
            "site_id": site_1_id,
        }
        ret = client.post(BUILDINGS_URL, json=building_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{BUILDINGS_URL}{building_1_id}")
        assert ret.status_code == 401

        # PUT
        building_1 = {
            "name": "Super Building 1",
        }
        ret = client.put(
            f"{BUILDINGS_URL}{building_1_id}",
            json=building_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{BUILDINGS_URL}{building_1_id}", headers={"If-Match": "Dummy-Etag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
