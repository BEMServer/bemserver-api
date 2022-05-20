"""About routes tests"""
import bemserver_core
import bemserver_api

import pytest

from tests.common import AuthHeader


ABOUT_URL = "/about/"


class TestAboutApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_about_api_as_admin_or_user(self, app, user, users):

        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET about info
            ret = client.get(ABOUT_URL)
            assert ret.status_code == 200
            assert ret.json == {
                "versions": {
                    "bemserver_core": bemserver_core.__version__,
                    "bemserver_api": bemserver_api.__version__,
                }
            }

    def test_about_api_as_anonym(self, app):

        client = app.test_client()

        # GET about info
        ret = client.get(ABOUT_URL)
        assert ret.status_code == 401
