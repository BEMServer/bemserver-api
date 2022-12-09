"""Events by spaces routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

EVENTS_BY_SPACES_URL = "/events_by_spaces/"
EVENTS_URL = "/events/"


class TestEventBySpaceApi:
    def test_events_by_spaces_api(self, app, users, spaces, events):

        creds = users["Chuck"]["creds"]
        event_1_id = events[0]
        event_2_id = events[1]
        space_1_id = spaces[0]
        space_2_id = spaces[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(EVENTS_BY_SPACES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ebs_1 = {
                "event_id": event_1_id,
                "space_id": space_1_id,
            }
            ret = client.post(EVENTS_BY_SPACES_URL, json=ebs_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ebs_1_id = ret_val.pop("id")
            ebs_1_etag = ret.headers["ETag"]
            assert ret_val == ebs_1

            # POST violating unique constraint
            ret = client.post(EVENTS_BY_SPACES_URL, json=ebs_1)
            assert ret.status_code == 409

            # POST event + space from different campaigns
            ebs = {
                "event_id": event_2_id,
                "space_id": space_1_id,
            }
            ret = client.post(EVENTS_BY_SPACES_URL, json=ebs)
            assert ret.status_code == 422
            ret_val = ret.json
            assert ret_val["errors"]["json"]["_schema"] == (
                "Event and space must be in same campaign"
            )

            # GET list
            ret = client.get(EVENTS_BY_SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == space_1_id

            # GET by id
            ret = client.get(f"{EVENTS_BY_SPACES_URL}{ebs_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ebs_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == ebs_1

            # POST
            ebs_2 = {
                "event_id": event_2_id,
                "space_id": space_2_id,
            }
            ret = client.post(EVENTS_BY_SPACES_URL, json=ebs_2)
            ret_val = ret.json
            ebs_2_id = ret_val.pop("id")

            # GET list
            ret = client.get(EVENTS_BY_SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                EVENTS_BY_SPACES_URL,
                query_string={"event_id": event_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ebs_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(f"{EVENTS_BY_SPACES_URL}{DUMMY_ID}")
            assert ret.status_code == 404

            # DELETE event cascade
            ret = client.get(f"{EVENTS_URL}{event_1_id}")
            event_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{EVENTS_URL}{event_1_id}", headers={"If-Match": event_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(f"{EVENTS_BY_SPACES_URL}{ebs_1_id}")
            assert ret.status_code == 404
            ret = client.delete(f"{EVENTS_BY_SPACES_URL}{ebs_2_id}")
            assert ret.status_code == 204

            # GET list
            ret = client.get(EVENTS_BY_SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{EVENTS_BY_SPACES_URL}{ebs_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_events_by_spaces_as_user_api(
        self, app, users, spaces, events, events_by_spaces
    ):

        user_creds = users["Active"]["creds"]
        event_1_id = events[0]
        event_2_id = events[1]
        space_1_id = spaces[0]
        space_2_id = spaces[1]
        ebs_1_id = events_by_spaces[0]
        ebs_2_id = events_by_spaces[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(EVENTS_BY_SPACES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ebs_1 = ret_val[0]
            assert ebs_1.pop("id") == ebs_1_id

            # GET by id
            ret = client.get(f"{EVENTS_BY_SPACES_URL}{ebs_1_id}")
            assert ret.status_code == 200
            ebs_1_etag = ret.headers["ETag"]

            # GET by id not in campaign scope
            ret = client.get(f"{EVENTS_BY_SPACES_URL}{ebs_2_id}")
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{EVENTS_BY_SPACES_URL}{ebs_1_id}",
                headers={"If-Match": ebs_1_etag},
            )
            assert ret.status_code == 204

            # POST
            ebs_3 = {
                "event_id": event_1_id,
                "space_id": space_1_id,
            }
            ret = client.post(EVENTS_BY_SPACES_URL, json=ebs_3)
            assert ret.status_code == 201
            ret_val = ret.json

            # POST not in campaign scope
            ebs = {
                "event_id": event_2_id,
                "space_id": space_2_id,
            }
            ret = client.post(EVENTS_BY_SPACES_URL, json=ebs)
            assert ret.status_code == 403

    def test_events_by_spaces_as_anonym_api(
        self, app, spaces, events, events_by_spaces
    ):
        event_1_id = events[0]
        space_2_id = spaces[1]
        ebs_1_id = events_by_spaces[0]

        client = app.test_client()

        # GET list
        ret = client.get(EVENTS_BY_SPACES_URL)
        assert ret.status_code == 401

        # POST
        ebs_3 = {
            "event_id": event_1_id,
            "space_id": space_2_id,
        }
        ret = client.post(EVENTS_BY_SPACES_URL, json=ebs_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{EVENTS_BY_SPACES_URL}{ebs_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{EVENTS_BY_SPACES_URL}{ebs_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
