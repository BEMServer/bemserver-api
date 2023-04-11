"""ST_DownloadWeatherDataBySites routes tests"""
from copy import deepcopy

import pytest

from tests.common import AuthHeader


DUMMY_ID = "69"

ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL = "/st_download_weather_data_by_sites/"


class TestST_DownloadWeatherDataBySitesApi:
    def test_st_download_weather_data_by_sites_api(self, app, users, campaigns, sites):
        creds = users["Chuck"]["creds"]
        campaign_1_id = campaigns[0]
        site_1_id = sites[0]
        site_2_id = sites[1]

        client = app.test_client()

        with AuthHeader(creds):
            # GET list
            ret = client.get(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL)
            assert ret.status_code == 200
            assert ret.json == []

            # POST
            st_cbc_1 = {"site_id": site_1_id}
            ret = client.post(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL, json=st_cbc_1)
            assert ret.status_code == 201
            ret_val = ret.json
            st_cbc_1_id = ret_val.pop("id")
            st_cbc_1_etag = ret.headers["ETag"]
            st_cbc_1_expected = deepcopy(st_cbc_1)
            st_cbc_1_expected["is_enabled"] = True
            assert ret_val == st_cbc_1_expected

            # POST violating unique constraint
            ret = client.post(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL, json=st_cbc_1)
            assert ret.status_code == 409

            # GET list
            ret = client.get(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_1_id

            # GET by id
            ret = client.get(f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}")
            assert ret.status_code == 200
            assert ret.headers["ETag"] == st_cbc_1_etag
            ret_val = ret.json
            ret_val.pop("id")
            assert ret_val == st_cbc_1_expected

            # PUT
            st_cbc_1_expected["is_enabled"] = False
            ret = client.put(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}",
                json={"is_enabled": False},
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            ret_val.pop("id")
            st_cbc_1_etag = ret.headers["ETag"]
            assert ret_val == st_cbc_1_expected

            # PUT wrong ID -> 404
            ret = client.put(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{DUMMY_ID}",
                json={"is_enabled": False},
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 404

            # POST site 2
            st_cbc_2 = {"site_id": site_2_id}
            ret = client.post(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL, json=st_cbc_2)
            ret_val = ret.json
            st_cbc_2_id = ret_val.pop("id")
            st_cbc_2_etag = ret.headers["ETag"]

            # GET list
            ret = client.get(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2

            # GET list with filters
            ret = client.get(
                ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL,
                query_string={"site_id": site_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_1_id

            # GET list (full), sort by site name
            ret = client.get(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}full",
                query_string={"sort": "+site_name"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 2
            assert ret_val[0]["id"] == st_cbc_1_id
            assert ret_val[0]["site_id"] == site_1_id
            assert not ret_val[0]["is_enabled"]
            assert ret_val[1]["id"] == st_cbc_2_id
            assert ret_val[1]["site_id"] == site_2_id
            assert ret_val[1]["is_enabled"]

            # GET list (full), sort by site name and filter by state
            ret = client.get(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}full",
                query_string={"is_enabled": True, "sort": "+site_name"},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_2_id
            assert ret_val[0]["site_id"] == site_2_id
            assert ret_val[0]["is_enabled"]

            # GET list (full), filter by campaign
            ret = client.get(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}full",
                query_string={"campaign_id": campaign_1_id},
            )
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_1_id
            assert ret_val[0]["site_id"] == site_1_id

            # DELETE wrong ID -> 404
            ret = client.delete(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{DUMMY_ID}",
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 404

            # DELETE
            ret = client.delete(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}",
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 204
            ret = client.delete(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_2_id}",
                headers={"If-Match": st_cbc_2_etag},
            )
            assert ret.status_code == 204

            # GET list
            ret = client.get(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 0

            # GET by id -> 404
            ret = client.get(f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}")
            assert ret.status_code == 404

    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaigns")
    def test_st_download_weather_data_by_sites_as_user_api(
        self, app, users, sites, st_download_weather_data_by_sites
    ):
        user_creds = users["Active"]["creds"]
        site_1_id = sites[0]
        st_cbc_1_id = st_download_weather_data_by_sites[0]
        st_cbc_2_id = st_download_weather_data_by_sites[1]

        client = app.test_client()

        with AuthHeader(user_creds):
            # GET list
            ret = client.get(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL)
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            st_cbc_1 = ret_val[0]
            assert st_cbc_1["id"] == st_cbc_1_id

            # POST
            st_cbc_3 = {"site_id": site_1_id}
            ret = client.post(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL, json=st_cbc_3)
            assert ret.status_code == 403

            # GET by id
            ret = client.get(f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}")
            assert ret.status_code == 200
            ret_val = ret.json
            assert ret_val["id"] == st_cbc_1_id
            st_cbc_1_etag = ret.headers["ETag"]
            ret = client.get(f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_2_id}")
            assert ret.status_code == 403

            # PUT
            ret = client.put(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}",
                json={"is_enabled": False},
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 403

            # DELETE
            ret = client.delete(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}",
                headers={"If-Match": st_cbc_1_etag},
            )
            assert ret.status_code == 403

            # GET list (full)
            ret = client.get(f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}full")
            assert ret.status_code == 200
            ret_val = ret.json
            assert len(ret_val) == 1
            assert ret_val[0]["id"] == st_cbc_1_id

            # GET list (full), filter by state is_enabled
            ret = client.get(
                f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}full",
                query_string={"is_enabled": False},
            )
            assert ret.status_code == 200
            assert len(ret.json) == 0

    def test_st_download_weather_data_by_sites_as_anonym_api(
        self, app, sites, st_download_weather_data_by_sites
    ):
        site_1_id = sites[0]
        st_cbc_1_id = st_download_weather_data_by_sites[0]

        client = app.test_client()

        # GET list
        ret = client.get(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL)
        assert ret.status_code == 401

        # POST
        st_cbc_3 = {"site_id": site_1_id}
        ret = client.post(ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL, json=st_cbc_3)
        assert ret.status_code == 401

        # GET by id
        ret = client.get(f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}")
        assert ret.status_code == 401

        # PUT
        ret = client.put(
            f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}",
            json={"is_enabled": False},
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # DELETE
        ret = client.delete(
            f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}{st_cbc_1_id}",
            headers={"If-Match": "Dummy-Etag"},
        )
        # ETag is wrong but we get rejected before ETag check anyway
        assert ret.status_code == 401

        # GET list (full)
        ret = client.get(f"{ST_DOWNLOAD_WEATHER_DATA_BY_SITES_URL}full")
        assert ret.status_code == 401
