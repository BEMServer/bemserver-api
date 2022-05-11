"""Storeys routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

STOREYS_URL = "/storeys/"


class TestStoreysApi:
    def test_storeys_api(self, app, users, campaigns, sites, buildings):

        creds = users["Chuck"]["creds"]
        campaign_2_id = campaigns[1]
        site_2_id = sites[1]
        building_1_id = buildings[0]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(STOREYS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            storey_1 = {
                "name": "Storey 1",
                "building_id": building_1_id,
            }
            ret = client.post(STOREYS_URL, json=storey_1)
            assert ret.status_code == 201
            ret_val = ret.json
            storey_1_id = ret_val.pop("id")
            storey_1_etag = ret.headers["ETag"]
            assert ret_val == storey_1

            # POST violating unique constraint
            ret = client.post(STOREYS_URL, json=storey_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(STOREYS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == storey_1_id

            # GET by id
            ret = client.get(f"{STOREYS_URL}{storey_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == storey_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == storey_1

            # PUT
            storey_1["description"] = "Fantastic storey"
            storey_1_put = storey_1.copy()
            del storey_1_put["building_id"]
            ret = client.put(
                f"{STOREYS_URL}{storey_1_id}",
                json=storey_1_put,
                headers={"If-Match": storey_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            storey_1_etag = ret.headers["ETag"]
            assert ret_val == storey_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{STOREYS_URL}{DUMMY_ID}",
                json=storey_1_put,
                headers={"If-Match": storey_1_etag},
            )
            assert ret.status_code == 404

            # POST storey 2
            storey_2 = {
                "name": "Storey 2",
                "building_id": building_1_id,
            }
            ret = client.post(STOREYS_URL, json=storey_2)
            ret_val = ret.json
            storey_2_id = ret_val.pop("id")
            storey_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            storey_1_put["name"] = storey_2["name"]
            ret = client.put(
                f"{STOREYS_URL}{storey_1_id}",
                json=storey_1_put,
                headers={"If-Match": storey_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(STOREYS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(STOREYS_URL, query_string={"name": "Storey 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == storey_1_id
            ret = client.get(STOREYS_URL, query_string={"campaign_id": campaign_2_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val
            ret = client.get(STOREYS_URL, query_string={"site_id": site_2_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{STOREYS_URL}{DUMMY_ID}", headers={"If-Match": storey_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{STOREYS_URL}{storey_1_id}", headers={"If-Match": storey_1_etag}
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{STOREYS_URL}{storey_2_id}", headers={"If-Match": storey_2_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(STOREYS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{STOREYS_URL}{storey_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_storeys_as_user_api(self, app, users, buildings, storeys):

        user_creds = users["Active"]["creds"]
        building_2_id = buildings[1]
        storey_1_id = storeys[0]
        storey_2_id = storeys[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(STOREYS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            storey_1 = ret_val[0]
            assert storey_1.pop("id") == storey_1_id

            # GET list with filters
            ret = client.get(STOREYS_URL, query_string={"name": "Storey 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == storey_1_id
            ret = client.get(STOREYS_URL, query_string={"name": "Storey 2"})
            assert ret.status_code == 200
            assert not ret.json

            # POST
            storey_3 = {
                "name": "Storey 3",
                "building_id": building_2_id,
            }
            ret = client.post(STOREYS_URL, json=storey_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{STOREYS_URL}{storey_1_id}")
            assert ret.status_code == 200
            storey_1_etag = ret.headers["ETag"]

            ret = client.get(f"{STOREYS_URL}{storey_2_id}")
            assert ret.status_code == 403

            # PUT
            storey_1["description"] = "Fantastic storey"
            storey_1_put = storey_1.copy()
            del storey_1_put["building_id"]
            ret = client.put(
                f"{STOREYS_URL}{storey_1_id}",
                json=storey_1_put,
                headers={"If-Match": storey_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{STOREYS_URL}{storey_1_id}", headers={"If-Match": storey_1_etag}
            )
            assert ret.status_code == 403

    def test_storeys_as_anonym_api(self, app, storeys, buildings):

        storey_1_id = storeys[0]
        building_1_id = buildings[0]

        client = app.test_client()

        # GET list
        ret = client.get(STOREYS_URL)
        assert ret.status_code == 401

        # POST
        storey_3 = {
            "name": "Storey 3",
            "building_id": building_1_id,
        }
        ret = client.post(STOREYS_URL, json=storey_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{STOREYS_URL}{storey_1_id}")
        assert ret.status_code == 401

        # PUT
        storey_1 = {
            "name": "Super Storey 1",
        }
        ret = client.put(
            f"{STOREYS_URL}{storey_1_id}",
            json=storey_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{STOREYS_URL}{storey_1_id}", headers={"If-Match": "Dummy-Etag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
