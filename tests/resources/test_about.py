"""About routes tests"""
import contextlib

import bemserver_core
import bemserver_api

import pytest

from tests.common import AuthHeader


ABOUT_URL = "/about/"


class TestAboutApi:
    @pytest.mark.parametrize("user", ("user", "admin", "anonym"))
    def test_about_api(self, app, user, users):

        if user == "user":
            auth_ctx = AuthHeader(users["Active"]["creds"])
        elif user == "admin":
            auth_ctx = AuthHeader(users["Chuck"]["creds"])
        else:
            auth_ctx = contextlib.nullcontext()

        client = app.test_client()

        with auth_ctx:

            # GET about info
            ret = client.get(ABOUT_URL)
            assert ret.status_code == 200
            assert ret.json == {
                "versions": {
                    "bemserver_core": bemserver_core.__version__,
                    "bemserver_api": bemserver_api.__version__,
                }
            }
