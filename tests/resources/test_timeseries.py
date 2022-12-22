"""Timeseries tests"""
import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

TIMESERIES_URL = "/timeseries/"
CAMPAIGNS_URL = "/campaigns/"
CAMPAIGN_SCOPES_URL = "/campaign_scopes/"


class TestTimeseriesApi:
    def test_timeseries_api(self, app, users, campaigns, campaign_scopes):

        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]
        campaign_2_id = campaigns[1]
        cs_1_id = campaign_scopes[0]
        cs_2_id = campaign_scopes[1]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            timeseries_1 = {
                "name": "Timeseries 1",
                "description": "Timeseries example 1",
                "campaign_id": campaign_1_id,
                "campaign_scope_id": cs_1_id,
                "unit_symbol": "°C",
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == 201
            ret_val = ret.json
            timeseries_1_id = ret_val.pop("id")
            timeseries_1_etag = ret.headers["ETag"]
            assert ret_val == timeseries_1

            # POST violating unique constraint
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == timeseries_1_id

            # GET by id
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == timeseries_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == timeseries_1

            # PUT
            del timeseries_1["description"]
            timeseries_1_put = timeseries_1.copy()
            del timeseries_1_put["campaign_id"]
            del timeseries_1_put["campaign_scope_id"]
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                json=timeseries_1_put,
                headers={"If-Match": timeseries_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            timeseries_1_etag = ret.headers["ETag"]
            assert ret_val == timeseries_1

            # PUT wrong ID -> 404
            ret = client.put(
                f"{TIMESERIES_URL}{DUMMY_ID}",
                json=timeseries_1_put,
                headers={"If-Match": timeseries_1_etag},
            )
            assert ret.status_code == 404

            # POST TS 2
            timeseries_2 = {
                "name": "Timeseries 2",
                "campaign_id": campaign_1_id,
                "campaign_scope_id": cs_2_id,
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_2)
            ret_val = ret.json

            # PUT violating unique constraint
            timeseries_1_put["name"] = timeseries_2["name"]
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                json=timeseries_1_put,
                headers={"If-Match": timeseries_1_etag},
            )
            assert ret.status_code == 409

            # GET list with filters
            ret = client.get(TIMESERIES_URL, query_string={"name": "Timeseries 1"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == timeseries_1_id
            ret = client.get(TIMESERIES_URL, query_string={"unit_symbol": "°C"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == timeseries_1_id
            ret = client.get(TIMESERIES_URL, query_string={"unit_symbol": "kWh"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # DELETE
            timeseries_3 = {
                "name": "Timeseries 3",
                "description": "Timeseries example 3",
                "campaign_id": campaign_2_id,
                "campaign_scope_id": cs_1_id,
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_3)
            ret_val = ret.json
            assert ret.status_code == 201
            timeseries_3_id = ret_val.pop("id")
            timeseries_3_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{TIMESERIES_URL}{timeseries_3_id}",
                headers={"If-Match": timeseries_3_etag},
            )
            assert ret.status_code == 204

            # DELETE campaign scope cascade
            ret = client.get(f"{CAMPAIGN_SCOPES_URL}{cs_1_id}")
            cs_1_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{CAMPAIGN_SCOPES_URL}{cs_1_id}", headers={"If-Match": cs_1_etag}
            )
            assert ret.status_code == 204

            # DELETE campaign cascade
            ret = client.get(f"{CAMPAIGNS_URL}{campaign_2_id}")
            campaign_2_etag = ret.headers["ETag"]
            ret = client.delete(
                f"{CAMPAIGNS_URL}{campaign_2_id}", headers={"If-Match": campaign_2_etag}
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # GET by id -> 404
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("timeseries_by_spaces")
    @pytest.mark.usefixtures("timeseries_by_zones")
    @pytest.mark.usefixtures("timeseries_by_events")
    def test_timeseries_filters_api(
        self,
        app,
        users,
        sites,
        buildings,
        storeys,
        spaces,
        zones,
        events,
    ):

        creds = users["Chuck"]["creds"]
        site_1_id = sites[0]
        building_1_id = buildings[0]
        storey_1_id = storeys[0]
        space_1_id = spaces[0]
        zone_1_id = zones[0]
        event_1_id = events[0]

        client = app.test_client()

        with AuthHeader(creds):
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            ret = client.get(f"{TIMESERIES_URL}by_site/{site_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(
                f"{TIMESERIES_URL}by_site/{site_1_id}",
                query_string={"recurse": True},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ret = client.get(f"{TIMESERIES_URL}by_building/{building_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(
                f"{TIMESERIES_URL}by_building/{building_1_id}",
                query_string={"recurse": True},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ret = client.get(f"{TIMESERIES_URL}by_storey/{storey_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(
                f"{TIMESERIES_URL}by_storey/{storey_1_id}",
                query_string={"recurse": True},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ret = client.get(f"{TIMESERIES_URL}by_space/{space_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ret = client.get(f"{TIMESERIES_URL}by_zone/{zone_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            ret = client.get(f"{TIMESERIES_URL}by_event/{event_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    def test_timeseries_as_user_api(
        self, app, users, timeseries, campaigns, campaign_scopes
    ):

        campaign_1_id = campaigns[0]
        cs_1_id = campaign_scopes[0]
        timeseries_1_id = timeseries[0]
        timeseries_2_id = timeseries[1]

        creds = users["Active"]["creds"]

        client = app.test_client()

        with AuthHeader(creds):

            # GET list
            ret = client.get(TIMESERIES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["campaign_id"] == campaign_1_id
            assert ret_val[0]["campaign_scope_id"] == cs_1_id
            assert ret_val[0]["id"] == timeseries_1_id

            # GET list using "in_name"
            ret = client.get(TIMESERIES_URL, query_string={"in_name": "Toto"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0
            ret = client.get(TIMESERIES_URL, query_string={"in_name": "series"})
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["campaign_id"] == campaign_1_id
            assert ret_val[0]["campaign_scope_id"] == cs_1_id
            assert ret_val[0]["id"] == timeseries_1_id

            # POST
            timeseries_1 = {
                "name": "Timeseries 1",
                "description": "Timeseries example 1",
                "campaign_id": campaign_1_id,
                "campaign_scope_id": cs_1_id,
            }
            ret = client.post(TIMESERIES_URL, json=timeseries_1)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
            assert ret.status_code == 200
            ts_1_etag = ret.headers["ETag"]

            # GET by id, user not in group
            ret = client.get(f"{TIMESERIES_URL}{timeseries_2_id}")
            assert ret.status_code == 403

            # PUT
            del timeseries_1["description"]
            del timeseries_1["campaign_id"]
            del timeseries_1["campaign_scope_id"]
            ret = client.put(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                json=timeseries_1,
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{TIMESERIES_URL}{timeseries_1_id}",
                headers={"If-Match": ts_1_etag},
            )
            # ETag is wrong but we get rejected before ETag check anyway
            assert ret.status_code == 403

    def test_timeseries_as_anonym_api(
        self, app, users, timeseries, campaigns, campaign_scopes
    ):

        campaign_1_id = campaigns[0]
        cs_1_id = campaign_scopes[0]
        timeseries_1_id = timeseries[0]

        client = app.test_client()

        # GET list
        ret = client.get(TIMESERIES_URL)
        assert ret.status_code == 401

        # POST
        timeseries_1 = {
            "name": "Timeseries 1",
            "description": "Timeseries example 1",
            "campaign_id": campaign_1_id,
            "campaign_scope_id": cs_1_id,
        }
        ret = client.post(TIMESERIES_URL, json=timeseries_1)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{TIMESERIES_URL}{timeseries_1_id}")
        assert ret.status_code == 401

        # PUT
        del timeseries_1["description"]
        del timeseries_1["campaign_id"]
        del timeseries_1["campaign_scope_id"]
        ret = client.put(
            f"{TIMESERIES_URL}{timeseries_1_id}",
            json=timeseries_1,
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{TIMESERIES_URL}{timeseries_1_id}",
            headers={"If-Match": "Dummy-ETag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401
