"""Input / Output tests"""
import contextlib
import io

import pytest

from tests.common import AuthHeader

INPUT_OUTPUT_URL = "/io/"
INPUT_OUTPUT_SITES_URL = f"{INPUT_OUTPUT_URL}sites"
INPUT_OUTPUT_TIMESERIES_URL = f"{INPUT_OUTPUT_URL}timeseries"
BUILDINGS_URL = "/buildings/"
TIMESERIES_URL = "/timeseries/"

DUMMY_ID = "69"


class TestInputOutputSites:
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.usefixtures("site_properties")
    @pytest.mark.usefixtures("building_properties")
    @pytest.mark.usefixtures("storey_properties")
    @pytest.mark.usefixtures("space_properties")
    @pytest.mark.usefixtures("zone_properties")
    def test_sites_csv_post(self, app, user, users, campaigns):

        campaign_1_id = campaigns[0]

        if user == "admin":
            creds = users["Chuck"]["creds"]
            auth_context = AuthHeader(creds)
        elif user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
        else:
            auth_context = contextlib.nullcontext()

        client = app.test_client()

        sites_csv = (
            "Name,Description,IFC_ID,Area\n"
            "Site 1,Great site 1,abcdefghijklmnopqrtsuv,1000\n"
            "Site 2,Great site 2,,2000\n"
        )
        buildings_csv = (
            "Name,Description,Site,IFC_ID,Area\n"
            "Building 1,Great building 1,Site 1,bcdefghijklmnopqrtsuvw,1000\n"
            "Building 2,Great building 2,Site 2,,2000\n"
        )
        storeys_csv = (
            "Name,Description,Site,Building,IFC_ID,Area\n"
            "Storey 1,Great storey 1,Site 1,Building 1,cdefghijklmnopqrtsuvwx,1000\n"
            "Storey 2,Great storey 2,Site 2,Building 2,,2000\n"
        )
        spaces_csv = (
            "Name,Description,Site,Building,Storey,IFC_ID,Area\n"
            "Storey 1,Great storey 1,Site 1,Building 1,Storey 1,"
            "defghijklmnopqrtsuvwxy,1000\n"
            "Storey 2,Great storey 2,Site 2,Building 2,Storey 2,"
            ",2000\n"
        )
        zones_csv = (
            "Name,Description,IFC_ID,Area\n"
            "Zone 1,Great zone 1,efghijklmnopqrtsuvwxyz,1000\n"
            "Zone 2,Great zone 2,,2000\n"
        )

        with auth_context:

            ret = client.post(
                INPUT_OUTPUT_SITES_URL,
                query_string={
                    "campaign_id": campaign_1_id,
                },
                data={
                    "sites_csv": (io.BytesIO(sites_csv.encode()), "sites.csv"),
                    "buildings_csv": (
                        io.BytesIO(buildings_csv.encode()),
                        "buildings.csv",
                    ),
                    "storeys_csv": (io.BytesIO(storeys_csv.encode()), "storeys.csv"),
                    "spaces_csv": (io.BytesIO(spaces_csv.encode()), "spaces.csv"),
                    "zones_csv": (io.BytesIO(zones_csv.encode()), "zones.csv"),
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 201
                ret = client.get(BUILDINGS_URL)
                assert ret.status_code == 200
                assert len(ret.json) == 2

    @pytest.mark.usefixtures("site_properties")
    @pytest.mark.usefixtures("building_properties")
    def test_sites_csv_post_sites_buildings(self, app, users, campaigns):

        campaign_1_id = campaigns[0]

        creds = users["Chuck"]["creds"]
        auth_context = AuthHeader(creds)

        client = app.test_client()

        sites_csv = (
            "Name,Description,IFC_ID,Area\n"
            "Site 1,Great site 1,,1000\n"
            "Site 2,Great site 2,,2000\n"
        )
        buildings_csv = (
            "Name,Description,Site,IFC_ID,Area\n"
            "Building 1,Great building 1,Site 1,,1000\n"
            "Building 2,Great building 2,Site 2,,2000\n"
        )

        with auth_context:

            ret = client.post(
                INPUT_OUTPUT_SITES_URL,
                query_string={
                    "campaign_id": campaign_1_id,
                },
                data={
                    "sites_csv": (io.BytesIO(sites_csv.encode()), "sites.csv"),
                    "buildings_csv": (
                        io.BytesIO(buildings_csv.encode()),
                        "buildings.csv",
                    ),
                },
            )
            assert ret.status_code == 201
            ret = client.get(BUILDINGS_URL)
            assert ret.status_code == 200
            assert len(ret.json) == 2

    @pytest.mark.parametrize(
        "buildings_csv",
        (
            # Missing column in header
            "Name,Description,Site",
            # Missing column in row
            "Name,Description,Site,IFC_ID\nBuilding 1,,",
            # Duplicate building
            "Name,Description,Site,IFC_ID\nBuilding 3,,Site 1,\nBuilding 3,,Site 1,",
            # Unknown site
            "Name,Description,Site,IFC_ID\nBuilding 1,,Dummy",
        ),
    )
    @pytest.mark.usefixtures("sites")
    def test_sites_csv_post_errors(self, app, users, campaigns, buildings_csv):

        campaign_1_id = campaigns[0]

        creds = users["Chuck"]["creds"]
        auth_context = AuthHeader(creds)

        client = app.test_client()

        with auth_context:

            ret = client.post(
                INPUT_OUTPUT_SITES_URL,
                query_string={
                    "campaign_id": campaign_1_id,
                },
                data={
                    "buildings_csv": (
                        io.BytesIO(buildings_csv.encode()),
                        "buildings.csv",
                    ),
                },
            )
            assert ret.status_code == 422

    def test_sites_csv_post_unknown_campaign(self, app, users):

        creds = users["Chuck"]["creds"]
        auth_context = AuthHeader(creds)

        client = app.test_client()

        sites_csv = (
            "Name,Description,IFC_ID\n"
            "Site 1,Great site 1,\n"
            "Site 1,Great site 2,\n"
        )

        with auth_context:

            ret = client.post(
                INPUT_OUTPUT_SITES_URL,
                query_string={
                    "campaign_id": DUMMY_ID,
                },
                data={
                    "sites_csv": (io.BytesIO(sites_csv.encode()), "sites.csv"),
                },
            )
            assert ret.status_code == 422
            ret_val = ret.json
            assert "campaign_id" in ret_val["errors"]["query"]


class TestInputOutputTimeseries:
    @pytest.mark.parametrize("user", ("admin", "user", "anonym"))
    @pytest.mark.usefixtures("users_by_user_groups")
    @pytest.mark.usefixtures("user_groups_by_campaign_scopes")
    @pytest.mark.usefixtures("sites")
    @pytest.mark.usefixtures("buildings")
    @pytest.mark.usefixtures("storeys")
    @pytest.mark.usefixtures("spaces")
    @pytest.mark.usefixtures("zones")
    def test_timeseries_csv_post(self, app, user, users, campaigns):

        campaign_1_id = campaigns[0]

        if user == "admin":
            creds = users["Chuck"]["creds"]
            auth_context = AuthHeader(creds)
        elif user == "user":
            creds = users["Active"]["creds"]
            auth_context = AuthHeader(creds)
        else:
            auth_context = contextlib.nullcontext()

        client = app.test_client()

        timeseries_csv = (
            "Name,Description,Unit,Campaign scope,Site,Building,"
            "Storey,Space,Zone,Min,Max\n"
            "Space_1_Temp,Temperature,°C,Campaign 1 - Scope 1,Site 1,Building 1,"
            "Storey 1,Space 1,Zone 1,-10,60\n"
            "Space_2_Temp,Temperature,°C,Campaign 1 - Scope 1,Site 1,Building 1,"
            "Storey 1,Space 1,Zone 1,-10,60\n"
        )

        with auth_context:

            ret = client.post(
                INPUT_OUTPUT_TIMESERIES_URL,
                query_string={
                    "campaign_id": campaign_1_id,
                },
                data={
                    "timeseries_csv": (
                        io.BytesIO(timeseries_csv.encode()),
                        "timeseries.csv",
                    ),
                },
            )
            if user == "anonym":
                assert ret.status_code == 401
            elif user == "user":
                assert ret.status_code == 403
            else:
                assert ret.status_code == 201
                ret = client.get(TIMESERIES_URL)
                assert ret.status_code == 200
                assert len(ret.json) == 2

    @pytest.mark.parametrize(
        "timeseries_csv",
        (
            # Missing column in header
            (
                "Name,Description,Unit,Campaign scope,\n"
                "Space_1_Temp,Temperature,°C,Campaign 1 - Scope 1,,,,,\n"
            ),
            # Duplicate timeseries
            (
                "Name,Description,Unit,Campaign scope,Site,Building,Storey,Space,Zone\n"
                "Space_1_Temp,Temperature,°C,Campaign 1 - Scope 1,,,,,\n"
                "Space_1_Temp,Temperature,°C,Campaign 1 - Scope 1,,,,,\n"
            ),
            # Unknown site
            (
                "Name,Description,Unit,Campaign scope,Site,Building,Storey,Space,Zone\n"
                "Space_1_Temp,Temperature,°C,Campaign 1 - Scope 1,Dummy,,,,\n"
            ),
        ),
    )
    @pytest.mark.usefixtures("campaign_scopes")
    def test_timeseries_csv_post_errors(self, app, users, campaigns, timeseries_csv):

        campaign_1_id = campaigns[0]

        creds = users["Chuck"]["creds"]
        auth_context = AuthHeader(creds)

        client = app.test_client()

        with auth_context:

            ret = client.post(
                INPUT_OUTPUT_TIMESERIES_URL,
                query_string={
                    "campaign_id": campaign_1_id,
                },
                data={
                    "timeseries_csv": (
                        io.BytesIO(timeseries_csv.encode()),
                        "timeseries.csv",
                    ),
                },
            )
            assert ret.status_code == 422

    def test_timeseries_csv_post_unknown_campaign(self, app, users):

        creds = users["Chuck"]["creds"]
        auth_context = AuthHeader(creds)

        client = app.test_client()

        timeseries_csv = (
            "Name,Description,Unit,Campaign scope,Site,Building,"
            "Storey,Space,Zone\n"
            "Space_1_Temp,Temperature,°C,Campaign 1 - Scope 1,Site 1,Building 1,"
            "Storey 1,Space 1,Zone 1\n"
            "Space_2_Temp,Temperature,°C,Campaign 1 - Scope 1,Site 1,Building 1,"
            "Storey 1,Space 1,Zone 1\n"
        )

        with auth_context:

            ret = client.post(
                INPUT_OUTPUT_TIMESERIES_URL,
                query_string={
                    "campaign_id": DUMMY_ID,
                },
                data={
                    "timeseries_csv": (
                        io.BytesIO(timeseries_csv.encode()),
                        "timeseries.csv",
                    ),
                },
            )
            assert ret.status_code == 422
            ret_val = ret.json
            assert "campaign_id" in ret_val["errors"]["query"]
