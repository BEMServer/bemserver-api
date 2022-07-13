"""Storey property data routes tests"""
import copy
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

STOREY_PROPERTY_DATA_URL = "/storey_property_data/"
STOREYS_URL = "/storeys/"


class TestStoreyPropertyDataApi:
    def test_storey_property_data_api(self, app, users, storeys, storey_properties):

        creds = users["Chuck"]["creds"]
        storey_1_id = storeys[0]
        storey_2_id = storeys[1]
        storey_p_1_id = storey_properties[0]
        storey_p_2_id = storey_properties[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(STOREY_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            spd_1 = {
                "storey_id": storey_1_id,
                "storey_property_id": storey_p_1_id,
                "value": "12",
            }
            ret = client.post(STOREY_PROPERTY_DATA_URL, json=spd_1)
            assert ret.status_code == 201
            ret_val = ret.json
            spd_1_id = ret_val.pop("id")
            spd_1_etag = ret.headers["ETag"]
            assert ret_val == spd_1

            # POST violating unique constraint
            ret = client.post(STOREY_PROPERTY_DATA_URL, json=spd_1)
            assert ret.status_code == 409

            # POST wrong value type
            spd_post = {
                "storey_id": storey_1_id,
                "storey_property_id": storey_p_2_id,
                "value": "wrong type",
            }
            ret = client.post(STOREY_PROPERTY_DATA_URL, json=spd_post)
            assert ret.status_code == 422

            # GET list
            ret = client.get(STOREY_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == storey_p_1_id

            # GET by id
            ret = client.get(f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == spd_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == spd_1

            # PUT
            spd_1["value"] = "69"
            ret = client.put(
                f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}",
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
                f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}",
                json=spd_1_put,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 422

            # PUT wrong ID -> 404
            ret = client.put(
                f"{STOREY_PROPERTY_DATA_URL}{DUMMY_ID}",
                json=spd_1,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            spd_2 = {
                "storey_id": storey_2_id,
                "storey_property_id": storey_p_2_id,
                "value": "42",
            }
            ret = client.post(STOREY_PROPERTY_DATA_URL, json=spd_2)
            ret_val = ret.json
            spd_2_id = ret_val.pop("id")
            spd_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            spd_1["storey_id"] = spd_2["storey_id"]
            spd_1["storey_property_id"] = spd_2["storey_property_id"]
            ret = client.put(
                f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}",
                json=spd_1,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(STOREY_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                STOREY_PROPERTY_DATA_URL,
                query_string={"storey_id": storey_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == spd_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{STOREY_PROPERTY_DATA_URL}{DUMMY_ID}",
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 404

            # DELETE storey cascade
            ret = client.get(f"{STOREYS_URL}{storey_1_id}")
            storey_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{STOREYS_URL}{storey_1_id}", headers={"If-Match": storey_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(
                f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}",
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{STOREY_PROPERTY_DATA_URL}{spd_2_id}",
                headers={"If-Match": spd_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(STOREY_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_storey_property_data_as_user_api(
        self, app, users, storeys, storey_properties, storey_property_data
    ):

        user_creds = users["Active"]["creds"]
        storey_1_id = storeys[0]
        storey_p_1_id = storey_properties[0]
        storey_p_1_id = storey_properties[0]
        spd_1_id = storey_property_data[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(STOREY_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            spd_1 = ret_val[0]
            assert spd_1.pop("id") == spd_1_id

            # POST
            spd_3 = {
                "storey_id": storey_1_id,
                "storey_property_id": storey_p_1_id,
                "value": "12",
            }
            ret = client.post(STOREY_PROPERTY_DATA_URL, json=spd_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}")
            assert ret.status_code == 200
            spd_1_etag = ret.headers["ETag"]

            # PUT
            spd_1["value"] = "69"
            ret = client.put(
                f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}",
                json=spd_1,
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}",
                headers={"If-Match": spd_1_etag},
            )
            assert ret.status_code == 403

    def test_storey_property_data_as_anonym_api(
        self, app, storeys, storey_properties, storey_property_data
    ):
        storey_1_id = storeys[0]
        storey_p_1_id = storey_properties[0]
        storey_p_2_id = storey_properties[1]
        spd_1_id = storey_property_data[0]

        client = app.test_client()

        # GET list
        ret = client.get(STOREY_PROPERTY_DATA_URL)
        assert ret.status_code == 401

        # POST
        spd_3 = {
            "storey_id": storey_1_id,
            "storey_property_id": storey_p_2_id,
            "value": "12",
        }
        ret = client.post(STOREY_PROPERTY_DATA_URL, json=spd_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}")
        assert ret.status_code == 401

        # PUT
        spd_1 = {
            "storey_id": storey_1_id,
            "storey_property_id": storey_p_1_id,
            "value": "12",
        }
        ret = client.put(
            f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}",
            json=spd_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{STOREY_PROPERTY_DATA_URL}{spd_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
