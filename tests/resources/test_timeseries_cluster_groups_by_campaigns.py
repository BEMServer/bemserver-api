"""Timeseries cluster group by campaign routes tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_CLUSTERS_URL = "/timeseries_clusters/"
TIMESERIES_CLUSTER_GROUPS_URL = "/timeseries_cluster_groups/"
TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL = "/timeseries_cluster_groups_by_campaigns/"


class TestTimeseriesClusterGroupByCampaignsApi:
    def test_timeseries_cluster_groups_by_campaigns_api(
        self, app, users, timeseries, timeseries_cluster_groups, campaigns
    ):

        ts_1_id = timeseries[0]
        tscg_1_id = timeseries_cluster_groups[0]
        tscg_2_id = timeseries_cluster_groups[1]
        campaign_1_id, campaign_2_id = campaigns

        creds = users["Chuck"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            tscgbc_1 = {
                "campaign_id": campaign_1_id,
                "timeseries_cluster_group_id": tscg_1_id,
            }
            ret = client.post(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL, json=tscgbc_1)
            assert ret.status_code == 201
            ret_val = ret.json
            tscgbc_1_id = ret_val.pop("id")
            tscgbc_1_etag = ret.headers["ETag"]

            # POST violating unique constraint
            ret = client.post(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL, json=tscgbc_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tscgbc_1_id

            # GET by id
            ret = client.get(
                f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_1_id}"
            )
            assert ret.status_code == 200
            assert ret.headers["ETag"] == tscgbc_1_etag

            # POST
            tscgbc_2 = {
                "campaign_id": campaign_2_id,
                "timeseries_cluster_group_id": tscg_2_id,
            }
            ret = client.post(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL, json=tscgbc_2)
            assert ret.status_code == 201
            ret_val = ret.json
            tscgbc_2_id = ret_val.pop("id")

            # GET list (filtered)
            ret = client.get(
                TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL,
                query_string={"timeseries_cluster_group_id": tscg_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tscgbc_1_id
            assert ret_val[0]["timeseries_cluster_group_id"] == tscg_1_id
            assert ret_val[0]["campaign_id"] == campaign_1_id
            ret = client.get(
                TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL,
                query_string={"campaign_id": campaign_2_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == tscgbc_2_id
            assert ret_val[0]["timeseries_cluster_group_id"] == tscg_2_id
            assert ret_val[0]["campaign_id"] == campaign_2_id
            ret = client.get(
                TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL,
                query_string={
                    "timeseries_cluster_group_id": tscg_1_id,
                    "campaign_id": campaign_2_id,
                },
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET TS list filtered by campaign
            ret = client.get(
                TIMESERIES_CLUSTERS_URL, query_string={"campaign_id": campaign_1_id}
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == ts_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{DUMMY_ID}"
            )
            assert ret.status_code == 404

            # DELETE TS group violating fkey constraint
            ret = client.get(f"{TIMESERIES_CLUSTER_GROUPS_URL}{tscg_1_id}")
            tscg_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{TIMESERIES_CLUSTER_GROUPS_URL}{tscg_1_id}",
                headers={"If-Match": tscg_1_etag},
            )
            assert ret.status_code == 409

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_1_id}"
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_2_id}"
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(
                f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_1_id}"
            )
            assert ret.status_code == 404

    @pytest.mark.usefixtures("timeseries_cluster_groups_by_users")
    @pytest.mark.usefixtures("users_by_campaigns")
    def test_timeseries_cluster_groups_by_campaigns_as_user_api(
        self,
        app,
        users,
        timeseries_cluster_groups,
        campaigns,
        timeseries_cluster_groups_by_campaigns,
    ):

        tscg_1_id = timeseries_cluster_groups[0]
        tscgbc_1_id = timeseries_cluster_groups_by_campaigns[0]
        tscgbc_2_id = timeseries_cluster_groups_by_campaigns[1]
        campaign_1_id = campaigns[0]
        campaign_1_id = campaigns[0]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 1
            assert ret.json[0]["id"] == tscgbc_1_id
            assert ret.json[0]["campaign_id"] == campaign_1_id
            assert ret.json[0]["timeseries_cluster_group_id"] == tscg_1_id

            # POST
            # We would get a 409 anyway since this association already exists.
            # But the 403 is triggered first.
            tscgbc = {
                "campaign_id": campaign_1_id,
                "timeseries_cluster_group_id": tscg_1_id,
            }
            ret = client.post(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL, json=tscgbc)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(
                f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_2_id}"
            )
            assert ret.status_code == 403

            # GET by id
            ret = client.get(
                f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_1_id}"
            )
            assert ret.status_code == 200

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_1_id}"
            )
            assert ret.status_code == 403

    def test_timeseries_cluster_groups_by_campaigns_as_anonym_api(
        self,
        app,
        users,
        timeseries_cluster_groups,
        campaigns,
        timeseries_cluster_groups_by_campaigns,
    ):

        tscg_1_id = timeseries_cluster_groups[0]
        tscgbc_1_id = timeseries_cluster_groups_by_campaigns[0]
        campaign_1_id = campaigns[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL)
        assert ret.status_code == 401

        # POST
        tscgbc = {
            "campaign_id": campaign_1_id,
            "timeseries_cluster_group_id": tscg_1_id,
        }
        ret = client.post(TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL, json=tscgbc)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_1_id}")
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_CLUSTER_GROUPS_BY_CAMPAIGNS_URL}{tscgbc_1_id}"
        )
        assert ret.status_code == 401
