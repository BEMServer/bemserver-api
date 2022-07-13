"""Building properties routes tests"""
from tests.common import AuthHeader


DUMMY_ID = "69"

BUILDING_PROPERTIES_URL = "/building_properties/"


class TestCampaignsApi:
    def test_building_properties_api(self, app, users, structural_element_properties):

        creds = users["Chuck"]["creds"]
        sep_1_id = structural_element_properties[0]
        sep_2_id = structural_element_properties[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(BUILDING_PROPERTIES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            building_p_1 = {
                "structural_element_property_id": sep_1_id,
            }
            ret = client.post(BUILDING_PROPERTIES_URL, json=building_p_1)
            assert ret.status_code == 201
            ret_val = ret.json
            building_p_1_id = ret_val.pop("id")
            building_p_1_etag = ret.headers["ETag"]
            sep = ret_val.pop("structural_element_property")
            assert sep == {"name": "Area", "value_type": "integer"}
            assert ret_val == building_p_1

            # POST violating unique constraint
            ret = client.post(BUILDING_PROPERTIES_URL, json=building_p_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(BUILDING_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == building_p_1_id

            # GET by id
            ret = client.get(f"{BUILDING_PROPERTIES_URL}{building_p_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == building_p_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            ret_val.pop("structural_element_property")
            assert ret_val == building_p_1

            # POST sep 2
            building_p_2 = {
                "structural_element_property_id": sep_2_id,
            }
            ret = client.post(BUILDING_PROPERTIES_URL, json=building_p_2)
            ret_val = ret.json
            building_p_2_id = ret_val.pop("id")

            # GET list
            ret = client.get(BUILDING_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                BUILDING_PROPERTIES_URL,
                query_string={"structural_element_property_id": sep_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == building_p_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{BUILDING_PROPERTIES_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(f"{BUILDING_PROPERTIES_URL}{building_p_1_id}")
            assert ret.status_code == 204
            ret = client.delete(f"{BUILDING_PROPERTIES_URL}{building_p_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(BUILDING_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{BUILDING_PROPERTIES_URL}{building_p_1_id}")
            assert ret.status_code == 404

    def test_building_properties_as_user_api(
        self, app, users, structural_element_properties, building_properties
    ):

        user_creds = users["Active"]["creds"]
        sep_1_id = structural_element_properties[0]
        building_p_1_id = building_properties[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(BUILDING_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            building_p_1 = ret_val[0]
            assert building_p_1.pop("id") == building_p_1_id

            # POST
            building_p_3 = {
                "structural_element_property_id": sep_1_id,
            }
            ret = client.post(BUILDING_PROPERTIES_URL, json=building_p_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{BUILDING_PROPERTIES_URL}{building_p_1_id}")
            assert ret.status_code == 200

            # DELETE
            ret = client.delete(f"{BUILDING_PROPERTIES_URL}{building_p_1_id}")
            assert ret.status_code == 403

    def test_building_properties_as_anonym_api(
        self, app, structural_element_properties, building_properties
    ):

        sep_1_id = structural_element_properties[0]
        building_p_1_id = building_properties[0]

        client = app.test_client()

        # GET list
        ret = client.get(BUILDING_PROPERTIES_URL)
        assert ret.status_code == 401

        # POST
        building_p_3 = {
            "structural_element_property_id": sep_1_id,
        }
        ret = client.post(BUILDING_PROPERTIES_URL, json=building_p_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{BUILDING_PROPERTIES_URL}{building_p_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(f"{BUILDING_PROPERTIES_URL}{building_p_1_id}")
        assert ret.status_code == 401
