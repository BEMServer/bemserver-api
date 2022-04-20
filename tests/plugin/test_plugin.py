"""Test plugin"""
import pytest

from tests.common import AuthHeader, TestConfig


TEST_PLUGIN_URL = "/plugins/enable_campaigns/"


class TestPluginConfig(TestConfig):
    PLUGINS = [
        "tests.plugin.plugin.TestPlugin",
    ]


class TestPlugin:
    @pytest.mark.parametrize("app", (TestPluginConfig,), indirect=True)
    def test_plugin_as_admin(self, app, users, campaigns):

        campaign_1_id = campaigns[0]

        client = app.test_client()

        with AuthHeader(users["Chuck"]["creds"]):

            # GET list
            ret = client.get(TEST_PLUGIN_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            ec_1 = {
                "campaign_id": campaign_1_id,
                "enabled": True,
            }
            ret = client.post(TEST_PLUGIN_URL, json=ec_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ec_1_id = ret_val.pop("id")
            ec_1_etag = ret.headers["ETag"]
            assert ret_val == ec_1

            # GET list
            ret = client.get(TEST_PLUGIN_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ec_1_id

            # GET by id
            ret = client.get(f"{TEST_PLUGIN_URL}{ec_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ec_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == ec_1

            # PUT
            ec_1["enabled"] = False
            ret = client.put(
                f"{TEST_PLUGIN_URL}{ec_1_id}",
                json=ec_1,
                headers={"If-Match": ec_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            ec_1_etag = ret.headers["ETag"]
            assert ret_val == ec_1

            # DELETE
            ret = client.delete(
                f"{TEST_PLUGIN_URL}{ec_1_id}", headers={"If-Match": ec_1_etag}
            )
            assert ret.status_code == 204

    @pytest.mark.parametrize("app", (TestPluginConfig,), indirect=True)
    def test_plugin_as_user(self, app, users, campaigns):

        campaign_1_id = campaigns[0]

        client = app.test_client()

        with AuthHeader(users["Chuck"]["creds"]):

            # POST
            ec_1 = {
                "campaign_id": campaign_1_id,
                "enabled": True,
            }
            ret = client.post(TEST_PLUGIN_URL, json=ec_1)
            assert ret.status_code == 201
            ret_val = ret.json
            ec_1_id = ret_val.pop("id")
            ec_1_etag = ret.headers["ETag"]
            assert ret_val == ec_1

        with AuthHeader(users["Active"]["creds"]):

            # GET list
            ret = client.get(TEST_PLUGIN_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ec_1_id

            # POST
            ec_1 = {
                "campaign_id": campaign_1_id,
                "enabled": True,
            }
            ret = client.post(TEST_PLUGIN_URL, json=ec_1)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TEST_PLUGIN_URL}{ec_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == ec_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == ec_1

            # PUT
            ec_1["enabled"] = False
            ret = client.put(
                f"{TEST_PLUGIN_URL}{ec_1_id}",
                json=ec_1,
                headers={"If-Match": ec_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TEST_PLUGIN_URL}{ec_1_id}", headers={"If-Match": ec_1_etag}
            )
            assert ret.status_code == 403
