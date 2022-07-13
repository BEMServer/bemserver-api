"""Space property data routes tests"""
import copy
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

SPACE_PROPERTY_DATA_URL = "/space_property_data/"
SPACES_URL = "/spaces/"


class TestSpacePropertyDataApi:
    def test_space_property_data_api(self, app, users, spaces, space_properties):

        creds = users["Chuck"]["creds"]
        space_1_id = spaces[0]
        space_2_id = spaces[1]
        space_p_1_id = space_properties[0]
        space_p_2_id = space_properties[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(SPACE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            spd_1 = {
                "space_id": space_1_id,
                "space_property_id": space_p_1_id,
                "value": "12",
            }
            ret = client.post(SPACE_PROPERTY_DATA_URL, json=spd_1)
            assert ret.status_code == 201
            ret_val = ret.json
            spd_1_id = ret_val.pop("id")
            spd_1_etag = ret.headers["ETag"]
            assert ret_val == spd_1

            # POST violating unique constraint
            ret = client.post(SPACE_PROPERTY_DATA_URL, json=spd_1)
            assert ret.status_code == 409

            # POST wrong value type
            spd_post = {
                "space_id": space_1_id,
                "space_property_id": space_p_2_id,
                "value": "wrong type",
            }
            ret = client.post(SPACE_PROPERTY_DATA_URL, json=spd_post)
            assert ret.status_code == 422

            # GET list
            ret = client.get(SPACE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == space_p_1_id

            # GET by id
            ret = client.get(f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == spd_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == spd_1

            # PUT
            spd_1["value"] = "69"
            ret = client.put(
                f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}",
                json=spd_1,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            spd_1_etag = ret.headers["ETag"]
            assert ret_val == spd_1

            # PUT wrong value type
            spd_1_put = copy.deepcopy(spd_1)
            spd_1_put["value"] = "wrong type"
            ret = client.put(
                f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}",
                json=spd_1_put,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 422

            # PUT wrong ID -> 404
            ret = client.put(
                f"{SPACE_PROPERTY_DATA_URL}{DUMMY_ID}",
                json=spd_1,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            spd_2 = {
                "space_id": space_2_id,
                "space_property_id": space_p_2_id,
                "value": "42",
            }
            ret = client.post(SPACE_PROPERTY_DATA_URL, json=spd_2)
            ret_val = ret.json
            spd_2_id = ret_val.pop("id")
            spd_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            spd_1["space_id"] = spd_2["space_id"]
            spd_1["space_property_id"] = spd_2["space_property_id"]
            ret = client.put(
                f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}",
                json=spd_1,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(SPACE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                SPACE_PROPERTY_DATA_URL,
                query_string={"space_id": space_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == spd_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{SPACE_PROPERTY_DATA_URL}{DUMMY_ID}",
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 404

            # DELETE space cascade
            ret = client.get(f"{SPACES_URL}{space_1_id}")
            space_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{SPACES_URL}{space_1_id}", headers={"If-Match": space_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(
                f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}",
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{SPACE_PROPERTY_DATA_URL}{spd_2_id}",
                headers={"If-Match": spd_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(SPACE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_space_property_data_as_user_api(
        self, app, users, spaces, space_properties, space_property_data
    ):

        user_creds = users["Active"]["creds"]
        space_1_id = spaces[0]
        space_p_1_id = space_properties[0]
        space_p_1_id = space_properties[0]
        spd_1_id = space_property_data[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(SPACE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            spd_1 = ret_val[0]
            assert spd_1.pop("id") == spd_1_id

            # POST
            spd_3 = {
                "space_id": space_1_id,
                "space_property_id": space_p_1_id,
                "value": "12",
            }
            ret = client.post(SPACE_PROPERTY_DATA_URL, json=spd_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}")
            assert ret.status_code == 200
            spd_1_etag = ret.headers["ETag"]

            # PUT
            spd_1["value"] = "69"
            ret = client.put(
                f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}",
                json=spd_1,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}",
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 403

    def test_space_property_data_as_anonym_api(
        self, app, spaces, space_properties, space_property_data
    ):
        space_1_id = spaces[0]
        space_p_1_id = space_properties[0]
        space_p_2_id = space_properties[1]
        spd_1_id = space_property_data[0]

        client = app.test_client()

        # GET list
        ret = client.get(SPACE_PROPERTY_DATA_URL)
        assert ret.status_code == 401

        # POST
        spd_3 = {
            "space_id": space_1_id,
            "space_property_id": space_p_2_id,
            "value": "12",
        }
        ret = client.post(SPACE_PROPERTY_DATA_URL, json=spd_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}")
        assert ret.status_code == 401

        # PUT
        spd_1 = {
            "space_id": space_1_id,
            "space_property_id": space_p_1_id,
            "value": "12",
        }
        ret = client.put(
            f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}",
            json=spd_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{SPACE_PROPERTY_DATA_URL}{spd_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
