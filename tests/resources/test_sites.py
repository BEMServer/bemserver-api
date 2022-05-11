"""Sites routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

SITES_URL = "/sites/"


class TestSitesApi:
    def test_sites_api(self, app, users, campaigns):

        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            site_1 = {
                "name": "Site 1",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(SITES_URL, json=site_1)
            assert ret.status_code == 201
            ret_val = ret.json
            site_1_id = ret_val.pop("id")
            site_1_etag = ret.headers["ETag"]
            assert ret_val == site_1

            # POST violating unique constraint
            ret = client.post(SITES_URL, json=site_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == site_1_id

            # GET by id
            ret = client.get(f"{SITES_URL}{site_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == site_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == site_1

            # PUT
            site_1["description"] = "Fantastic site"
            site_1_put = site_1.copy()
            del site_1_put["campaign_id"]
            ret = client.put(
                f"{SITES_URL}{site_1_id}",
                json=site_1_put,
                headers={"If-Match": site_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            site_1_etag = ret.headers["ETag"]
            assert ret_val == site_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{SITES_URL}{DUMMY_ID}",
                json=site_1_put,
                headers={"If-Match": site_1_etag},
            )
            assert ret.status_code == 404

            # POST site 2
            site_2 = {
                "name": "Site 2",
                "campaign_id": campaign_1_id,
            }
            ret = client.post(SITES_URL, json=site_2)
            ret_val = ret.json
            site_2_id = ret_val.pop("id")
            site_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            site_1_put["name"] = site_2["name"]
            ret = client.put(
                f"{SITES_URL}{site_1_id}",
                json=site_1_put,
                headers={"If-Match": site_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(SITES_URL, query_string={"name": "Site 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == site_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{SITES_URL}{DUMMY_ID}", headers={"If-Match": site_1_etag}
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{SITES_URL}{site_1_id}", headers={"If-Match": site_1_etag}
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{SITES_URL}{site_2_id}", headers={"If-Match": site_2_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{SITES_URL}{site_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_sites_as_user_api(self, app, users, campaigns, sites):

        user_creds = users["Active"]["creds"]
        campaign_2_id = campaigns[1]
        site_1_id = sites[0]
        site_2_id = sites[1]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            site_1 = ret_val[0]
            assert site_1.pop("id") == site_1_id

            # GET list with filters
            ret = client.get(SITES_URL, query_string={"name": "Site 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == site_1_id
            ret = client.get(SITES_URL, query_string={"name": "Site 2"})
            assert ret.status_code == 200
            assert not ret.json

            # POST
            site_3 = {
                "name": "Site 3",
                "campaign_id": campaign_2_id,
            }
            ret = client.post(SITES_URL, json=site_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{SITES_URL}{site_1_id}")
            assert ret.status_code == 200
            site_1_etag = ret.headers["ETag"]

            ret = client.get(f"{SITES_URL}{site_2_id}")
            assert ret.status_code == 403

            # PUT
            site_1["description"] = "Fantastic site"
            site_1_put = site_1.copy()
            del site_1_put["campaign_id"]
            ret = client.put(
                f"{SITES_URL}{site_1_id}",
                json=site_1_put,
                headers={"If-Match": site_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{SITES_URL}{site_1_id}", headers={"If-Match": site_1_etag}
            )
            assert ret.status_code == 403

    def test_sites_as_anonym_api(self, app, sites, campaigns):

        site_1_id = sites[0]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        # GET list
        ret = client.get(SITES_URL)
        assert ret.status_code == 401

        # POST
        site_3 = {
            "name": "Site 3",
            "campaign_id": campaign_1_id,
        }
        ret = client.post(SITES_URL, json=site_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{SITES_URL}{site_1_id}")
        assert ret.status_code == 401

        # PUT
        site_1 = {
            "name": "Super Site 1",
        }
        ret = client.put(
            f"{SITES_URL}{site_1_id}",
            json=site_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{SITES_URL}{site_1_id}", headers={"If-Match": "Dummy-Etag"}
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
