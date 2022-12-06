"""Event categories tests"""
from tests.common import AuthHeader


DUMMY_ID = "69"

EVENT_CATEGORIES_URL = "/event_categories/"


class TestEventCategoriesApi:
    def test_event_categories_api(self, app, users):

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENT_CATEGORIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            nb_categ = len(ret_val)

            # POST
            event_categ_1 = {
                "name": "Custom category 1",
                "description": "Short description",
            }
            ret = client.post(EVENT_CATEGORIES_URL, json=event_categ_1)
            assert ret.status_code == 201
            ret_val = ret.json
            event_categ_1_id = ret_val.pop("id")
            event_categ_1_etag = ret.headers["ETag"]

            # POST violating unique constraint
            ret = client.post(EVENT_CATEGORIES_URL, json=event_categ_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(EVENT_CATEGORIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_categ + 1

            # GET by id
            ret = client.get(f"{EVENT_CATEGORIES_URL}{event_categ_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == event_categ_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == event_categ_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{EVENT_CATEGORIES_URL}{DUMMY_ID}",
                json=event_categ_1,
                headers={"If-Match": event_categ_1_etag},
            )
            assert ret.status_code == 404

            # PUT
            event_categ_1["description"] = "Longer description"
            ret = client.put(
                f"{EVENT_CATEGORIES_URL}{event_categ_1_id}",
                json=event_categ_1,
                headers={"If-Match": event_categ_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            event_categ_1_etag = ret.headers["ETag"]

            # POST
            event_categ_2 = {
                "name": "Custom category 2",
            }
            ret = client.post(EVENT_CATEGORIES_URL, json=event_categ_2)
            ret_val = ret.json

            # GET list
            ret = client.get(EVENT_CATEGORIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_categ + 2

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{EVENT_CATEGORIES_URL}{DUMMY_ID}",
                headers={"If-Match": event_categ_1_etag},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{EVENT_CATEGORIES_URL}{event_categ_1_id}",
                headers={"If-Match": event_categ_1_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENT_CATEGORIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == nb_categ + 1

            # GET by id -> 404
            ret = client.get(f"{EVENT_CATEGORIES_URL}{event_categ_1_id}")
            assert ret.status_code == 404

    def test_event_categories_as_user_api(self, app, users, event_categories):

        user_creds = users["Active"]["creds"]
        event_categ_1_id = event_categories[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(EVENT_CATEGORIES_URL)
            assert ret.status_code == 200

            # POST
            event_categ = {
                "name": "Custom category 1",
                "description": "Short description",
            }
            ret = client.post(EVENT_CATEGORIES_URL, json=event_categ)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{EVENT_CATEGORIES_URL}{event_categ_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            event_categ_1 = ret_val
            event_categ_1_etag = ret.headers["ETag"]

            # PUT
            ret = client.put(
                f"{EVENT_CATEGORIES_URL}{event_categ_1_id}",
                json=event_categ_1,
                headers={"If-Match": event_categ_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{EVENT_CATEGORIES_URL}{event_categ_1_id}",
                headers={"If-Match": event_categ_1_etag},
            )
            assert ret.status_code == 403

    def test_event_categories_as_anonym_api(self, app, event_categories):

        event_categ_1_id = event_categories[0]

        client = app.test_client()

        # GET list
        ret = client.get(EVENT_CATEGORIES_URL)
        assert ret.status_code == 401

        # POST
        event_categ = {
            "name": "Custom category 1",
            "description": "Short description",
        }
        ret = client.post(EVENT_CATEGORIES_URL, json=event_categ)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENT_CATEGORIES_URL}{event_categ_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(f"{EVENT_CATEGORIES_URL}{event_categ_1_id}", json=event_categ)

        # DELETE
        ret = client.delete(f"{EVENT_CATEGORIES_URL}{event_categ_1_id}")
        assert ret.status_code == 401
