"""Energy tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ENERGIES_URL = "/energies/"
ENERGY_END_USES_URL = "/energy_end_uses/"
ENERGY_PRODUCTION_TECHNOLOGIES_URL = "/energy_production_technologies/"


class TestEnergiesApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_energies_api_as_admin_or_user(self, app, user, users):
        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.get(ENERGIES_URL)
            assert ret.status_code == 200
            assert "all" in [e["name"] for e in ret.json]

    def test_energies_api_as_anonym(self, app):
        client = app.test_client()

        ret = client.get(ENERGIES_URL)
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


class TestEnergyProductionTechnologysApi:
    @pytest.mark.parametrize("user", ("user", "admin"))
    def test_energy_production_technologies_api_as_admin_or_user(
        self, app, user, users
    ):
        if user == "user":
            creds = users["Active"]["creds"]
        else:
            creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.get(ENERGY_PRODUCTION_TECHNOLOGIES_URL)
            assert ret.status_code == 200
            assert "all" in [e["name"] for e in ret.json]

    def test_enery_production_technologies_api_as_anonym(self, app):
        client = app.test_client()

        ret = client.get(ENERGY_PRODUCTION_TECHNOLOGIES_URL)
        assert ret.status_code == 401
