"""Event levels tests"""
import pytest

from tests.common import AuthHeader


EVENT_LEVELS_URL = "/event_levels/"


class TestEventLevelsApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_event_levels_api_as_admin_or_user(self, app, user, users):

        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET level list
            ret = client.get(EVENT_LEVELS_URL)
            assert ret.status_code == 200
            assert len(ret.json)

    def test_event_levels_api_as_anonym(self, app):

        client = app.test_client()

        ret = client.get(EVENT_LEVELS_URL)
        assert ret.status_code == 401
