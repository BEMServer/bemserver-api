"""Building property data routes tests"""
import copy
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

BUILDING_PROPERTY_DATA_URL = "/building_property_data/"
BUILDINGS_URL = "/buildings/"


class TestBuildingPropertyDataApi:
    def test_building_property_data_api(
        self, app, users, buildings, building_properties
    ):

        creds = users["Chuck"]["creds"]
        building_1_id = buildings[0]
        building_2_id = buildings[1]
        building_p_1_id = building_properties[0]
        building_p_2_id = building_properties[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(BUILDING_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            bpd_1 = {
                "building_id": building_1_id,
                "building_property_id": building_p_1_id,
                "value": "12",
            }
            ret = client.post(BUILDING_PROPERTY_DATA_URL, json=bpd_1)
            assert ret.status_code == 201
            ret_val = ret.json
            bpd_1_id = ret_val.pop("id")
            bpd_1_etag = ret.headers["ETag"]
            assert ret_val == bpd_1

            # POST violating unique constraint
            ret = client.post(BUILDING_PROPERTY_DATA_URL, json=bpd_1)
            assert ret.status_code == 409

            # POST wrong value type
            bpd_post = {
                "building_id": building_1_id,
                "building_property_id": building_p_2_id,
                "value": "wrong type",
            }
            ret = client.post(BUILDING_PROPERTY_DATA_URL, json=bpd_post)
            assert ret.status_code == 422

            # GET list
            ret = client.get(BUILDING_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == building_p_1_id

            # GET by id
            ret = client.get(f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == bpd_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == bpd_1

            # PUT
            bpd_1["value"] = "69"
            ret = client.put(
                f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}",
                json=bpd_1,
                headers={"If-Match": bpd_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            bpd_1_etag = ret.headers["ETag"]
            assert ret_val == bpd_1

            # PUT wrong value type
            bpd_1_put = copy.deepcopy(bpd_1)
            bpd_1_put["value"] = "wrong type"
            ret = client.put(
                f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}",
                json=bpd_1_put,
                headers={"If-Match": bpd_1_etag},
            )
            assert ret.status_code == 422

            # PUT wrong ID -> 404
            ret = client.put(
                f"{BUILDING_PROPERTY_DATA_URL}{DUMMY_ID}",
                json=bpd_1,
                headers={"If-Match": bpd_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            bpd_2 = {
                "building_id": building_2_id,
                "building_property_id": building_p_2_id,
                "value": "42",
            }
            ret = client.post(BUILDING_PROPERTY_DATA_URL, json=bpd_2)
            ret_val = ret.json
            bpd_2_id = ret_val.pop("id")
            bpd_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            bpd_1["building_id"] = bpd_2["building_id"]
            bpd_1["building_property_id"] = bpd_2["building_property_id"]
            ret = client.put(
                f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}",
                json=bpd_1,
                headers={"If-Match": bpd_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(BUILDING_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                BUILDING_PROPERTY_DATA_URL,
                query_string={"building_id": building_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == bpd_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{BUILDING_PROPERTY_DATA_URL}{DUMMY_ID}",
                headers={"If-Match": bpd_1_etag},
            )
            assert ret.status_code == 404

            # DELETE building cascade
            ret = client.get(f"{BUILDINGS_URL}{building_1_id}")
            building_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{BUILDINGS_URL}{building_1_id}", headers={"If-Match": building_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(
                f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}",
                headers={"If-Match": bpd_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{BUILDING_PROPERTY_DATA_URL}{bpd_2_id}",
                headers={"If-Match": bpd_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(BUILDING_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_building_property_data_as_user_api(
        self, app, users, buildings, building_properties, building_property_data
    ):

        user_creds = users["Active"]["creds"]
        building_1_id = buildings[0]
        building_p_1_id = building_properties[0]
        building_p_1_id = building_properties[0]
        bpd_1_id = building_property_data[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(BUILDING_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            bpd_1 = ret_val[0]
            assert bpd_1.pop("id") == bpd_1_id

            # POST
            bpd_3 = {
                "building_id": building_1_id,
                "building_property_id": building_p_1_id,
                "value": "12",
            }
            ret = client.post(BUILDING_PROPERTY_DATA_URL, json=bpd_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}")
            assert ret.status_code == 200
            bpd_1_etag = ret.headers["ETag"]

            # PUT
            bpd_1["value"] = "69"
            ret = client.put(
                f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}",
                json=bpd_1,
                headers={"If-Match": bpd_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}",
                headers={"If-Match": bpd_1_etag},
            )
            assert ret.status_code == 403

    def test_building_property_data_as_anonym_api(
        self, app, buildings, building_properties, building_property_data
    ):
        building_1_id = buildings[0]
        building_p_1_id = building_properties[0]
        building_p_2_id = building_properties[1]
        bpd_1_id = building_property_data[0]

        client = app.test_client()

        # GET list
        ret = client.get(BUILDING_PROPERTY_DATA_URL)
        assert ret.status_code == 401

        # POST
        bpd_3 = {
            "building_id": building_1_id,
            "building_property_id": building_p_2_id,
            "value": "12",
        }
        ret = client.post(BUILDING_PROPERTY_DATA_URL, json=bpd_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}")
        assert ret.status_code == 401

        # PUT
        bpd_1 = {
            "building_id": building_1_id,
            "building_property_id": building_p_1_id,
            "value": "12",
        }
        ret = client.put(
            f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}",
            json=bpd_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{BUILDING_PROPERTY_DATA_URL}{bpd_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
