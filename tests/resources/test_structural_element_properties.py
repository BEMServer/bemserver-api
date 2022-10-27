"""Structural element properties routes tests"""
import copy

from tests.common import AuthHeader


DUMMY_ID = "69"

STRUCTURAL_ELEMENT_PROPERTIES_URL = "/structural_element_properties/"


class TestStructuralElementPropertiesApi:
    def test_structural_element_properties_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(STRUCTURAL_ELEMENT_PROPERTIES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            sep_1 = {
                "name": "Area",
                "value_type": "integer",
            }
            ret = client.post(STRUCTURAL_ELEMENT_PROPERTIES_URL, json=sep_1)
            assert ret.status_code == 201
            ret_val = ret.json
            sep_1_id = ret_val.pop("id")
            sep_1_etag = ret.headers["ETag"]
            assert ret_val == sep_1

            # POST violating unique constraint
            ret = client.post(STRUCTURAL_ELEMENT_PROPERTIES_URL, json=sep_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(STRUCTURAL_ELEMENT_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == sep_1_id

            # GET by id
            ret = client.get(f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == sep_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == sep_1

            # PUT
            sep_1["description"] = "Fantastic sep"
            sep_1_put = copy.deepcopy(sep_1)
            del sep_1_put["value_type"]
            ret = client.put(
                f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}",
                json=sep_1_put,
                headers={"If-Match": sep_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            sep_1_etag = ret.headers["ETag"]
            assert ret_val == sep_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{DUMMY_ID}",
                json=sep_1_put,
                headers={"If-Match": sep_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            sep_2 = {
                "name": "Volume",
                "unit_symbol": "L",
            }
            ret = client.post(STRUCTURAL_ELEMENT_PROPERTIES_URL, json=sep_2)
            assert ret.status_code == 201
            ret_val = ret.json
            assert ret_val["value_type"] == "string"
            sep_2_id = ret_val.pop("id")
            sep_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            sep_2_put = copy.deepcopy(sep_2)
            sep_2_put["name"] = sep_1["name"]
            ret = client.put(
                f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_2_id}",
                json=sep_2_put,
                headers={"If-Match": sep_2_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(STRUCTURAL_ELEMENT_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                STRUCTURAL_ELEMENT_PROPERTIES_URL, query_string={"name": "Area"}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == sep_1_id
            ret = client.get(
                STRUCTURAL_ELEMENT_PROPERTIES_URL,
                query_string={"value_type": "integer"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == sep_1_id
            ret = client.get(
                STRUCTURAL_ELEMENT_PROPERTIES_URL,
                query_string={"value_type": "boolean"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(
                STRUCTURAL_ELEMENT_PROPERTIES_URL,
                query_string={"unit_symbol": "L"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ret = client.get(
                STRUCTURAL_ELEMENT_PROPERTIES_URL,
                query_string={"unit_symbol": "kWh"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{DUMMY_ID}",
                headers={"If-Match": sep_1_etag},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}",
                headers={"If-Match": sep_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_2_id}",
                headers={"If-Match": sep_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(STRUCTURAL_ELEMENT_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}")
            assert ret.status_code == 404

    def test_structural_element_as_user_api(
        self, app, users, structural_element_properties
    ):

        user_creds = users["Active"]["creds"]
        sep_1_id = structural_element_properties[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(STRUCTURAL_ELEMENT_PROPERTIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 4

            # POST
            sep_3 = {
                "name": "Temperature setpoint",
                "value_type": "float",
            }
            ret = client.post(STRUCTURAL_ELEMENT_PROPERTIES_URL, json=sep_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}")
            assert ret.status_code == 200
            sep_1 = ret.json
            del sep_1["id"]
            sep_1_etag = ret.headers["ETag"]

            # PUT
            sep_1_put = copy.deepcopy(sep_1)
            del sep_1_put["value_type"]
            sep_1_put["description"] = "Fantastic sep"
            ret = client.put(
                f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}",
                json=sep_1_put,
                headers={"If-Match": sep_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}",
                headers={"If-Match": sep_1_etag},
            )
            assert ret.status_code == 403

    def test_structural_element_as_anonym_api(self, app, structural_element_properties):

        sep_1_id = structural_element_properties[0]

        client = app.test_client()

        # GET list
        ret = client.get(STRUCTURAL_ELEMENT_PROPERTIES_URL)
        assert ret.status_code == 401

        # POST
        sep_3 = {
            "name": "Temperature setpoint",
            "value_type": "float",
        }
        ret = client.post(STRUCTURAL_ELEMENT_PROPERTIES_URL, json=sep_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}")
        assert ret.status_code == 401

        # PUT
        sep_1 = {
            "name": "Gross surface",
        }
        ret = client.put(
            f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}",
            json=sep_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{STRUCTURAL_ELEMENT_PROPERTIES_URL}{sep_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
