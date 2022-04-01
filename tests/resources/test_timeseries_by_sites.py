"""Timeseries by sites routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_BY_SITES_URL = "/timeseries_by_sites/"
SITES_URL = "/sites/"


class TestTimeseriesBySiteApi:
    def test_timeseries_by_sites_api(self, app, users, sites, timeseries):

        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]
        site_2_id = sites[1]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tbs_1 = {
                "site_id": site_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_SITES_URL, json=tbs_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tbs_1_id = ret_val.pop("id")
            tbs_1_etag = ret.headers["ETag"]
            assert ret_val == tbs_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_BY_SITES_URL, json=tbs_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tbs_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == tbs_1

            # PUT
            tbs_1["timeseries_id"] = ts_2_id
            ret = client.put(
                f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}",
                json=tbs_1,
                headers={"If-Match": tbs_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            tbs_1_etag = ret.headers["ETag"]
            assert ret_val == tbs_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_BY_SITES_URL}{DUMMY_ID}",
                json=tbs_1,
                headers={"If-Match": tbs_1_etag},
            )
            assert ret.status_code == 404

            # POST sep 2
            tbs_2 = {
                "site_id": site_2_id,
                "timeseries_id": ts_2_id,
            }
            ret = client.post(TIMESERIES_BY_SITES_URL, json=tbs_2)
            ret_val = ret.json
            tbs_2_id = ret_val.pop("id")
            tbs_2_etag = ret.headers["ETag"]

            # PUT violating unique constraint
            tbs_1["site_id"] = tbs_2["site_id"]
            tbs_1["timeseries_id"] = tbs_2["timeseries_id"]
            ret = client.put(
                f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}",
                json=tbs_1,
                headers={"If-Match": tbs_1_etag},
            )
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                TIMESERIES_BY_SITES_URL,
                query_string={"site_id": site_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tbs_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{TIMESERIES_BY_SITES_URL}{DUMMY_ID}",
                headers={"If-Match": tbs_1_etag},
            )
            assert ret.status_code == 404

            # DELETE site cascade
            ret = client.get(f"{SITES_URL}{site_1_id}")
            site_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{SITES_URL}{site_1_id}", headers={"If-Match": site_1_etag}
            )
            assert ret.status_code == 204

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}",
                headers={"If-Match": tbs_1_etag},
            )
            assert ret.status_code == 404
            ret = client.delete(
                f"{TIMESERIES_BY_SITES_URL}{tbs_2_id}",
                headers={"If-Match": tbs_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.parametrize("timeseries", (4,), indirect=True)
    def test_timeseries_by_sites_as_user_api(
        self, app, users, sites, timeseries, timeseries_by_sites
    ):

        user_creds = users["Active"]["creds"]
        site_1_id = sites[0]
        ts_1_id = timeseries[0]
        ts_3_id = timeseries[2]
        tbs_1_id = timeseries_by_sites[0]

        client = app.test_client()

        with AuthHeader(user_creds):

            # GET list
            ret = client.get(TIMESERIES_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            tbs_1 = ret_val[0]
            assert tbs_1.pop("id") == tbs_1_id

            # POST
            tbs_3 = {
                "site_id": site_1_id,
                "timeseries_id": ts_1_id,
            }
            ret = client.post(TIMESERIES_BY_SITES_URL, json=tbs_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}")
            assert ret.status_code == 200
            tbs_1_etag = ret.headers["ETag"]

            # PUT
            tbs_1["timeseries_id"] = ts_3_id
            ret = client.put(
                f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}",
                json=tbs_1,
                headers={"If-Match": tbs_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}",
                headers={"If-Match": tbs_1_etag},
            )
            assert ret.status_code == 403

    def test_timeseries_by_sites_as_anonym_api(
        self, app, sites, timeseries, timeseries_by_sites
    ):
        site_1_id = sites[0]
        ts_1_id = timeseries[0]
        ts_2_id = timeseries[1]
        tbs_1_id = timeseries_by_sites[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_BY_SITES_URL)
        assert ret.status_code == 401

        # POST
        tbs_3 = {
            "site_id": site_1_id,
            "timeseries_id": ts_2_id,
        }
        ret = client.post(TIMESERIES_BY_SITES_URL, json=tbs_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}")
        assert ret.status_code == 401

        # PUT
        tbs_1 = {
            "site_id": site_1_id,
            "timeseries_id": ts_1_id,
        }
        ret = client.put(
            f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}",
            json=tbs_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_BY_SITES_URL}{tbs_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
