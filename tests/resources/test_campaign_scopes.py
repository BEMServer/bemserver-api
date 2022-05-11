"""Campaign scopes routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

CAMPAIGN_SCOPES_URL = "/campaign_scopes/"
CAMPAIGNS_URL = "/campaigns/"


class TestCampaignScopesApi:
    def test_campaign_scopes_api(self, app, users, campaigns):

        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            cs_1 = {
                "name": "Campaign scope 1",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(CAMPAIGN_SCOPES_URL, json=cs_1)
            assert ret.status_code == 201
            ret_val = ret.json
            cs_1_id = ret_val.pop("id")
            cs_1_etag = ret.headers["ETag"]
            assert ret_val == cs_1

            # POST violating unique constraint
            ret = client.post(CAMPAIGN_SCOPES_URL, json=cs_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == cs_1_id

            # GET by id
            ret = client.get(f"{CAMPAIGN_SCOPES_URL}{cs_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == cs_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == cs_1

            # PUT
            cs_1["description"] = "Fantastic campaign"
            cs_1_put = cs_1.copy()
            del cs_1_put["campaign_id"]
            ret = client.put(
                f"{CAMPAIGN_SCOPES_URL}{cs_1_id}",
                json=cs_1_put,
                headers={"If-Match": cs_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            cs_1_etag = ret.headers["ETag"]
            assert ret_val == cs_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{CAMPAIGN_SCOPES_URL}{DUMMY_ID}",
                json=cs_1_put,
                headers={"If-Match": cs_1_etag},
            )
            assert ret.status_code == 404

            # POST campaign_scope 2
            cs_2 = {
                "name": "Campaign scope 2",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(CAMPAIGN_SCOPES_URL, json=cs_2)
            ret_val = ret.json
            cs_2_id = ret_val.pop("id")
            cs_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            cs_1_put["name"] = cs_2["name"]
            ret = client.put(
                f"{CAMPAIGN_SCOPES_URL}{cs_1_id}",
                json=cs_1_put,
                headers={"If-Match": cs_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                CAMPAIGN_SCOPES_URL, query_string={"name": "Campaign scope 1"}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == cs_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{CAMPAIGN_SCOPES_URL}{DUMMY_ID}", headers={"If-Match": cs_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{CAMPAIGN_SCOPES_URL}{cs_2_id}", headers={"If-Match": cs_2_etag}
            )
            assert ret.status_code == 204

            # DELETE campaign cascade
            ret = client.get(f"{CAMPAIGNS_URL}{campaign_1_id}")
            campaign_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{CAMPAIGNS_URL}{campaign_1_id}", headers={"If-Match": campaign_1_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{CAMPAIGN_SCOPES_URL}{cs_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_campaign_scopes_as_user_api(self, app, users, campaigns, campaign_scopes):

        user_creds = users["Active"]["creds"]
        campaign_1_id = campaigns[0]
        cs_1_id = campaign_scopes[0]
        cs_2_id = campaign_scopes[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(CAMPAIGN_SCOPES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            cs_1 = ret_val[0]
            assert cs_1.pop("id") == cs_1_id

            # GET list with filters
            ret = client.get(
                CAMPAIGN_SCOPES_URL, query_string={"name": "Campaign 1 - Scope 1"}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == cs_1_id
            ret = client.get(
                CAMPAIGN_SCOPES_URL, query_string={"name": "Campaign 2 - Scope 1"}
            )
            assert ret.status_code == 200
            assert not ret.json

            # POST
            cs_3 = {
                "name": "Campaign 1 - Scope 2",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(CAMPAIGN_SCOPES_URL, json=cs_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{CAMPAIGN_SCOPES_URL}{cs_1_id}")
            assert ret.status_code == 200
            cs_1_etag = ret.headers["ETag"]

            ret = client.get(f"{CAMPAIGN_SCOPES_URL}{cs_2_id}")
            assert ret.status_code == 403

            # PUT
            cs_1["description"] = "Fantastic campaign"
            cs_1_put = cs_1.copy()
            del cs_1_put["campaign_id"]
            ret = client.put(
                f"{CAMPAIGN_SCOPES_URL}{cs_1_id}",
                json=cs_1_put,
                headers={"If-Match": cs_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{CAMPAIGN_SCOPES_URL}{cs_1_id}", headers={"If-Match": cs_1_etag}
            )
            assert ret.status_code == 403

    def test_campaign_scopes_as_anonym_api(self, app, campaign_scopes):

        cs_1_id = campaign_scopes[0]

        client = app.test_client()

        # GET list
        ret = client.get(CAMPAIGN_SCOPES_URL)
        assert ret.status_code == 401

        # POST
        cs_3 = {
            "name": "Campaign scope 3",
        }
        ret = client.post(CAMPAIGN_SCOPES_URL, json=cs_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{CAMPAIGN_SCOPES_URL}{cs_1_id}")
        assert ret.status_code == 401

        # PUT
        cs_1 = {
            "name": "Super campaign scope 1",
        }
        ret = client.put(
            f"{CAMPAIGN_SCOPES_URL}{cs_1_id}",
            json=cs_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{CAMPAIGN_SCOPES_URL}{cs_1_id}", headers={"If-Match": "Dummy-Etag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
