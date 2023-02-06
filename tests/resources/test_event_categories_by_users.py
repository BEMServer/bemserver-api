"""Event categories by users routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

EVENT_CATEGORIES_BY_USERS_URL = "/event_categories_by_users/"


class TestEventCategoryByUserApi:
    def test_event_categories_by_users_api(self, app, users, event_categories):
        creds = users["Chuck"]["creds"]
        ec_1_id = event_categories[0]
        ec_2_id = event_categories[1]
        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(EVENT_CATEGORIES_BY_USERS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ecbu_1 = {
                "category_id": ec_1_id,
                "user_id": user_1_id,
                "notification_level": "WARNING",
            }
            ret = client.post(EVENT_CATEGORIES_BY_USERS_URL, json=ecbu_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ecbu_1_id = ret_val.pop("id")
            ecbu_1_etag = ret.headers["ETag"]
            assert ret_val == ecbu_1

            # POST violating unique constraint
            ret = client.post(EVENT_CATEGORIES_BY_USERS_URL, json=ecbu_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(EVENT_CATEGORIES_BY_USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ecbu_1_id

            # GET by id
            ret = client.get(f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ecbu_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == ecbu_1

            # PUT
            ecbu_1["notification_level"] = "INFO"
            del ecbu_1["user_id"]
            ret = client.put(
                f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_1_id}",
                json=ecbu_1,
                headers={"If-Match": ecbu_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ecbu_1_etag = ret.headers["ETag"]

            # PUT wrong ID -> 404
            ret = client.put(
                f"{EVENT_CATEGORIES_BY_USERS_URL}{DUMMY_ID}",
                json=ecbu_1,
                headers={"If-Match": ecbu_1_etag},
            )
            assert ret.status_code == 404

            # POST
            ecbu_2 = {
                "category_id": ec_2_id,
                "user_id": user_2_id,
                "notification_level": "DEBUG",
            }
            ret = client.post(EVENT_CATEGORIES_BY_USERS_URL, json=ecbu_2)
            ret_val = ret.json

            # GET list
            ret = client.get(EVENT_CATEGORIES_BY_USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                EVENT_CATEGORIES_BY_USERS_URL,
                query_string={"category_id": ec_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ecbu_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{EVENT_CATEGORIES_BY_USERS_URL}{DUMMY_ID}",
                headers={"If-Match": "Dummy-ETag"},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_1_id}",
                headers={"If-Match": ecbu_1_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENT_CATEGORIES_BY_USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1

            # GET by id -> 404
            ret = client.get(f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_event_categories_by_users_as_user_api(
        self, app, users, event_categories, event_categories_by_users
    ):
        user_creds = users["Active"]["creds"]
        ec_2_id = event_categories[1]
        user_1_id = users["Active"]["id"]
        user_2_id = users["Inactive"]["id"]
        ecbu_1_id = event_categories_by_users[0]
        ecbu_2_id = event_categories_by_users[1]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(EVENT_CATEGORIES_BY_USERS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ecbu_1 = ret_val[0]
            assert ecbu_1.pop("id") == ecbu_1_id

            # GET by id
            ret = client.get(f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_1_id}")
            assert ret.status_code == 200

            # GET by id not owner
            ret = client.get(f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_2_id}")
            assert ret.status_code == 403

            # POST
            ecbu_3 = {
                "category_id": ec_2_id,
                "user_id": user_1_id,
                "notification_level": "WARNING",
            }
            ret = client.post(EVENT_CATEGORIES_BY_USERS_URL, json=ecbu_3)
            assert ret.status_code == 201
            ret_val = ret.json
            ecbu_3_id = ret_val["id"]
            ecbu_3_etag = ret.headers["ETag"]

            # POST not owner
            ecbu = {
                "category_id": ec_2_id,
                "user_id": user_2_id,
                "notification_level": "WARNING",
            }
            ret = client.post(EVENT_CATEGORIES_BY_USERS_URL, json=ecbu)
            assert ret.status_code == 403

            # PUT
            ecbu_3["notification_level"] = "INFO"
            del ecbu_3["user_id"]
            ret = client.put(
                f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_3_id}",
                json=ecbu_3,
                headers={"If-Match": ecbu_3_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ecbu_3_etag = ret.headers["ETag"]

            # PUT not owner
            ret = client.put(
                f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_2_id}",
                json=ecbu_3,
                headers={"If-Match": "Dummy-ETag"},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_3_id}",
                headers={"If-Match": ecbu_3_etag},
            )
            assert ret.status_code == 204

            # DELETE not owner
            ret = client.delete(
                f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_2_id}",
                headers={"If-Match": "Dummy-ETag"},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

    def test_event_categories_by_users_as_anonym_api(
        self, app, buildings, events, event_categories_by_users
    ):
        ec_1_id = events[0]
        user_2_id = buildings[1]
        ecbu_1_id = event_categories_by_users[0]

        client = app.test_client()

        # GET list
        ret = client.get(EVENT_CATEGORIES_BY_USERS_URL)
        assert ret.status_code == 401

        # POST
        ecbu_3 = {
            "category_id": ec_1_id,
            "user_id": user_2_id,
        }
        ret = client.post(EVENT_CATEGORIES_BY_USERS_URL, json=ecbu_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_1_id}")
        assert ret.status_code == 401

        # PUT
        del ecbu_3["user_id"]
        ret = client.put(
            f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_1_id}",
            json=ecbu_3,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{EVENT_CATEGORIES_BY_USERS_URL}{ecbu_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
