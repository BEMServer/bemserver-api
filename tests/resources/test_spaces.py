"""Spaces routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

SPACES_URL = "/spaces/"


class TestSpacesApi:
    def test_spaces_api(self, app, users, campaigns, sites, buildings, storeys):

        creds = users["Chuck"]["creds"]
        campaign_2_id = campaigns[1]
        site_2_id = sites[1]
        building_2_id = buildings[1]
        storey_1_id = storeys[0]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(SPACES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            space_1 = {
                "name": "Space 1",
                "storey_id": storey_1_id,
            }
            ret = client.post(SPACES_URL, json=space_1)
            assert ret.status_code == 201
            ret_val = ret.json
            space_1_id = ret_val.pop("id")
            space_1_etag = ret.headers["ETag"]
            assert ret_val == space_1

            # POST violating unique constraint
            ret = client.post(SPACES_URL, json=space_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == space_1_id

            # GET by id
            ret = client.get(f"{SPACES_URL}{space_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == space_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == space_1

            # PUT
            space_1["description"] = "Fantastic space"
            space_1_put = space_1.copy()
            del space_1_put["storey_id"]
            ret = client.put(
                f"{SPACES_URL}{space_1_id}",
                json=space_1_put,
                headers={"If-Match": space_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            space_1_etag = ret.headers["ETag"]
            assert ret_val == space_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{SPACES_URL}{DUMMY_ID}",
                json=space_1_put,
                headers={"If-Match": space_1_etag},
            )
            assert ret.status_code == 404

            # POST space 2
            space_2 = {
                "name": "Space 2",
                "storey_id": storey_1_id,
            }
            ret = client.post(SPACES_URL, json=space_2)
            ret_val = ret.json
            space_2_id = ret_val.pop("id")
            space_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            space_1_put["name"] = space_2["name"]
            ret = client.put(
                f"{SPACES_URL}{space_1_id}",
                json=space_1_put,
                headers={"If-Match": space_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(SPACES_URL, query_string={"name": "Space 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == space_1_id
            ret = client.get(SPACES_URL, query_string={"campaign_id": campaign_2_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val
            ret = client.get(SPACES_URL, query_string={"site_id": site_2_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val
            ret = client.get(SPACES_URL, query_string={"building_id": building_2_id})
            assert ret.status_code == 200
            ret_val = ret.json
            assert not ret_val

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{SPACES_URL}{DUMMY_ID}", headers={"If-Match": space_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{SPACES_URL}{space_1_id}", headers={"If-Match": space_1_etag}
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{SPACES_URL}{space_2_id}", headers={"If-Match": space_2_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{SPACES_URL}{space_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_spaces_as_user_api(self, app, users, storeys, spaces):

        user_creds = users["Active"]["creds"]
        storey_2_id = storeys[1]
        space_1_id = spaces[0]
        space_2_id = spaces[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            space_1 = ret_val[0]
            assert space_1.pop("id") == space_1_id

            # GET list with filters
            ret = client.get(SPACES_URL, query_string={"name": "Space 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == space_1_id
            ret = client.get(SPACES_URL, query_string={"name": "Space 2"})
            assert ret.status_code == 200
            assert not ret.json

            # POST
            space_3 = {
                "name": "Space 3",
                "storey_id": storey_2_id,
            }
            ret = client.post(SPACES_URL, json=space_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{SPACES_URL}{space_1_id}")
            assert ret.status_code == 200
            space_1_etag = ret.headers["ETag"]

            ret = client.get(f"{SPACES_URL}{space_2_id}")
            assert ret.status_code == 403

            # PUT
            space_1["description"] = "Fantastic space"
            space_1_put = space_1.copy()
            del space_1_put["storey_id"]
            ret = client.put(
                f"{SPACES_URL}{space_1_id}",
                json=space_1_put,
                headers={"If-Match": space_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{SPACES_URL}{space_1_id}", headers={"If-Match": space_1_etag}
            )
            assert ret.status_code == 403

    def test_spaces_as_anonym_api(self, app, spaces, storeys):

        space_1_id = spaces[0]
        storey_1_id = storeys[0]

        client = app.test_client()

        # GET list
        ret = client.get(SPACES_URL)
        assert ret.status_code == 401

        # POST
        space_3 = {
            "name": "Space 3",
            "storey_id": storey_1_id,
        }
        ret = client.post(SPACES_URL, json=space_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{SPACES_URL}{space_1_id}")
        assert ret.status_code == 401

        # PUT
        space_1 = {
            "name": "Super Space 1",
        }
        ret = client.put(
            f"{SPACES_URL}{space_1_id}",
            json=space_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{SPACES_URL}{space_1_id}", headers={"If-Match": "Dummy-Etag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
