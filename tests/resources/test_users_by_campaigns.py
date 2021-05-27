"""User by campaign routes tests"""
DUMMY_ID = "69"

USERS_URL = "/users/"
CAMPAIGNS_URL = "/campaigns/"
USERS_BY_CAMPAIGNS_URL = "/usersbycampaigns/"


class TestUsersByCampaignsApi:

    def test_users_by_campaigns_api(self, app, users, campaigns):

        user_1_id, user_2_id = users
        campaign_1_id, campaign_2_id = campaigns

        client = app.test_client()

        # GET list
        ret = client.get(USERS_BY_CAMPAIGNS_URL)
        assert ret.status_code == 200
        assert ret.json == []

        # POST
        ubc_1 = {"campaign_id": campaign_1_id, "user_id": user_1_id}
        ret = client.post(USERS_BY_CAMPAIGNS_URL, json=ubc_1)
        assert ret.status_code == 201
        ret_val = ret.json
        ubc_1_id = ret_val.pop("id")
        ubc_1_etag = ret.headers["ETag"]

        # POST violating unique constraint
        ret = client.post(USERS_BY_CAMPAIGNS_URL, json=ubc_1)
        assert ret.status_code == 409

        # GET list
        ret = client.get(USERS_BY_CAMPAIGNS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == ubc_1_id

        # GET by id
        ret = client.get(f"{USERS_BY_CAMPAIGNS_URL}{ubc_1_id}")
        assert ret.status_code == 200
        assert ret.headers["ETag"] == ubc_1_etag

        # POST
        ubc_2 = {"campaign_id": campaign_2_id, "user_id": user_2_id}
        ret = client.post(USERS_BY_CAMPAIGNS_URL, json=ubc_2)
        assert ret.status_code == 201
        ret_val = ret.json
        ubc_2_id = ret_val.pop("id")

        # GET list (filtered)
        ret = client.get(
            USERS_BY_CAMPAIGNS_URL,
            query_string={"user_id": user_1_id}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == ubc_1_id
        assert ret_val[0]["user_id"] == user_1_id
        assert ret_val[0]["campaign_id"] == user_1_id
        ret = client.get(
            USERS_BY_CAMPAIGNS_URL,
            query_string={"campaign_id": campaign_2_id}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 1
        assert ret_val[0]["id"] == ubc_2_id
        assert ret_val[0]["user_id"] == user_2_id
        assert ret_val[0]["campaign_id"] == user_2_id
        ret = client.get(
            USERS_BY_CAMPAIGNS_URL,
            query_string={"user_id": user_1_id, "campaign_id": campaign_2_id}
        )
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 0

        # DELETE wrong ID -> 404
        ret = client.delete(f"{USERS_BY_CAMPAIGNS_URL}{DUMMY_ID}")
        assert ret.status_code == 404

        # DELETE user violating fkey constraint
        ret = client.get(f"{USERS_URL}{user_1_id}")
        user_1_etag = ret.headers['ETag']
        ret = client.delete(
            f"{USERS_URL}{user_1_id}",
            headers={'If-Match': user_1_etag}
        )
        assert ret.status_code == 409

        # DELETE campaign violating fkey constraint
        ret = client.get(f"{CAMPAIGNS_URL}{campaign_1_id}")
        campaign_1_etag = ret.headers['ETag']
        ret = client.delete(
            f"{CAMPAIGNS_URL}{campaign_1_id}",
            headers={'If-Match': campaign_1_etag}
        )
        assert ret.status_code == 409

        # DELETE
        ret = client.delete(f"{USERS_BY_CAMPAIGNS_URL}{ubc_1_id}")
        assert ret.status_code == 204
        ret = client.delete(f"{USERS_BY_CAMPAIGNS_URL}{ubc_2_id}")
        assert ret.status_code == 204

        # GET list
        ret = client.get(USERS_BY_CAMPAIGNS_URL)
        assert ret.status_code == 200
        ret_val = ret.json
        assert len(ret_val) == 0

        # GET by id -> 404
        ret = client.get(f"{USERS_BY_CAMPAIGNS_URL}{ubc_1_id}")
        assert ret.status_code == 404
