"""Energy tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ENERGY_SOURCES_URL = "/energy_sources/"
ENERGY_END_USES_URL = "/energy_end_uses/"


class TestEnergySourcesApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_energy_sources_api_as_admin_or_user(self, app, user, users):

        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.get(ENERGY_SOURCES_URL)
            assert ret.status_code == 200
            assert "all" in [e["name"] for e in ret.json]

    def test_enery_sources_api_as_anonym(self, app):

        client = app.test_client()

        ret = client.get(ENERGY_SOURCES_URL)
        assert ret.status_code == 401


class TestEnergyEndUsesApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_energy_end_uses_api_as_admin_or_user(self, app, user, users):

        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.get(ENERGY_END_USES_URL)
            assert ret.status_code == 200
            assert "all" in [e["name"] for e in ret.json]

    def test_enery_end_uses_api_as_anonym(self, app):

        client = app.test_client()

        ret = client.get(ENERGY_END_USES_URL)
        assert ret.status_code == 401
