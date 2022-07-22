"""Zone property data routes tests"""
import copy
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ZONE_PROPERTY_DATA_URL = "/zone_property_data/"


class TestZonePropertyDataApi:
    def test_zone_property_data_api(self, app, users, zones, zone_properties):

        creds = users["Chuck"]["creds"]
        zone_1_id = zones[0]
        zone_2_id = zones[1]
        zone_p_1_id = zone_properties[0]
        zone_p_2_id = zone_properties[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(ZONE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            zpd_1 = {
                "zone_id": zone_1_id,
                "zone_property_id": zone_p_1_id,
                "value": "12",
            }
            ret = client.post(ZONE_PROPERTY_DATA_URL, json=zpd_1)
            assert ret.status_code == 201
            ret_val = ret.json
            zpd_1_id = ret_val.pop("id")
            zpd_1_etag = ret.headers["ETag"]
            assert ret_val == zpd_1

            # POST violating unique constraint
            ret = client.post(ZONE_PROPERTY_DATA_URL, json=zpd_1)
            assert ret.status_code == 409

            # POST wrong value type
            zpd_post = {
                "zone_id": zone_1_id,
                "zone_property_id": zone_p_2_id,
                "value": "wrong type",
            }
            ret = client.post(ZONE_PROPERTY_DATA_URL, json=zpd_post)
            assert ret.status_code == 422

            # GET list
            ret = client.get(ZONE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == zone_p_1_id

            # GET by id
            ret = client.get(f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == zpd_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == zpd_1

            # PUT
            zpd_1["value"] = "69"
            ret = client.put(
                f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}",
                json=zpd_1,
                headers={"If-Match": zpd_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            zpd_1_etag = ret.headers["ETag"]
            assert ret_val == zpd_1

            # PUT wrong value type
            zpd_1_put = copy.deepcopy(zpd_1)
            zpd_1_put["value"] = "wrong type"
            ret = client.put(
                f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}",
                json=zpd_1_put,
                headers={"If-Match": zpd_1_etag},
            )
            assert ret.status_code == 422

            # PUT wrong ID -> 404
            ret = client.put(
                f"{ZONE_PROPERTY_DATA_URL}{DUMMY_ID}",
                json=zpd_1,
                headers={"If-Match": zpd_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            zpd_2 = {
                "zone_id": zone_2_id,
                "zone_property_id": zone_p_2_id,
                "value": "42",
            }
            ret = client.post(ZONE_PROPERTY_DATA_URL, json=zpd_2)
            ret_val = ret.json
            zpd_2_id = ret_val.pop("id")
            zpd_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            zpd_1["zone_id"] = zpd_2["zone_id"]
            zpd_1["zone_property_id"] = zpd_2["zone_property_id"]
            ret = client.put(
                f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}",
                json=zpd_1,
                headers={"If-Match": zpd_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(ZONE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                ZONE_PROPERTY_DATA_URL,
                query_string={"zone_id": zone_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == zpd_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{ZONE_PROPERTY_DATA_URL}{DUMMY_ID}",
                headers={"If-Match": zpd_1_etag},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}",
                headers={"If-Match": zpd_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{ZONE_PROPERTY_DATA_URL}{zpd_2_id}",
                headers={"If-Match": zpd_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(ZONE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_zone_property_data_as_user_api(
        self, app, users, zones, zone_properties, zone_property_data
    ):

        user_creds = users["Active"]["creds"]
        zone_1_id = zones[0]
        zone_p_1_id = zone_properties[0]
        zone_p_1_id = zone_properties[0]
        zpd_1_id = zone_property_data[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(ZONE_PROPERTY_DATA_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            zpd_1 = ret_val[0]
            assert zpd_1.pop("id") == zpd_1_id

            # POST
            zpd_3 = {
                "zone_id": zone_1_id,
                "zone_property_id": zone_p_1_id,
                "value": "12",
            }
            ret = client.post(ZONE_PROPERTY_DATA_URL, json=zpd_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}")
            assert ret.status_code == 200
            zpd_1_etag = ret.headers["ETag"]

            # PUT
            zpd_1["value"] = "69"
            ret = client.put(
                f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}",
                json=zpd_1,
                headers={"If-Match": zpd_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}",
                headers={"If-Match": zpd_1_etag},
            )
            assert ret.status_code == 403

    def test_zone_property_data_as_anonym_api(
        self, app, zones, zone_properties, zone_property_data
    ):
        zone_1_id = zones[0]
        zone_p_1_id = zone_properties[0]
        zone_p_2_id = zone_properties[1]
        zpd_1_id = zone_property_data[0]

        client = app.test_client()

        # GET list
        ret = client.get(ZONE_PROPERTY_DATA_URL)
        assert ret.status_code == 401

        # POST
        zpd_3 = {
            "zone_id": zone_1_id,
            "zone_property_id": zone_p_2_id,
            "value": "12",
        }
        ret = client.post(ZONE_PROPERTY_DATA_URL, json=zpd_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}")
        assert ret.status_code == 401

        # PUT
        zpd_1 = {
            "zone_id": zone_1_id,
            "zone_property_id": zone_p_1_id,
            "value": "12",
        }
        ret = client.put(
            f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}",
            json=zpd_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{ZONE_PROPERTY_DATA_URL}{zpd_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
