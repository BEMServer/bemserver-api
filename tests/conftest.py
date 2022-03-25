"""Global conftest"""
import base64
import datetime as dt

import flask.testing

from bemserver_core.database import db
from bemserver_core.authorization import OpenBar
from bemserver_core import model
from bemserver_core.testutils import setup_db

import pytest
from pytest_postgresql import factories as ppf

from bemserver_api import create_app

from tests.common import TestConfig, AUTH_HEADER


postgresql_proc = ppf.postgresql_proc(
    postgres_options=(
        "-c shared_preload_libraries='timescaledb' "
        "-c timescaledb.telemetry_level=off"
    )
)
postgresql = ppf.postgresql("postgresql_proc")


class TestClient(flask.testing.FlaskClient):
    def open(self, *args, **kwargs):
        auth_header = AUTH_HEADER.get()
        if auth_header:
            (kwargs.setdefault("headers", {}).setdefault("Authorization", auth_header))
        return super().open(*args, **kwargs)


@pytest.fixture
def database(postgresql):
    yield from setup_db(postgresql)


@pytest.fixture(params=(TestConfig,))
def app(request, database):
    class AppConfig(request.param):
        SQLALCHEMY_DATABASE_URI = database.url

    application = create_app(AppConfig)
    application.test_client_class = TestClient
    yield application


USERS = (
    ("Chuck", "N0rris", "chuck@test.com", True, True),
    ("Active", "@ctive", "active@test.com", False, True),
    ("Inactive", "in@ctive", "inactive@test.com", False, False),
)


@pytest.fixture(params=(USERS,))
def users(database, request):
    with OpenBar():
        ret = {}
        for user in request.param:
            name, password, email, is_admin, is_active = user
            user = model.User.new(
                name=name, email=email, is_admin=is_admin, is_active=is_active
            )
            user.set_password(password)
            creds = base64.b64encode(f"{email}:{password}".encode()).decode()
            invalid_creds = base64.b64encode(f"{email}:bad_pwd".encode()).decode()
            ret[name] = {"user": user, "creds": creds, "invalid_creds": invalid_creds}
        db.session.commit()
        # Set id after commit
        for user in ret.values():
            user["id"] = user["user"].id
    return ret


@pytest.fixture
def user_groups(database):
    with OpenBar():
        user_group_1 = model.UserGroup.new(
            name="User group 1",
        )
        user_group_2 = model.UserGroup.new(
            name="User group 2",
        )
        db.session.commit()
    return (user_group_1.id, user_group_2.id)


@pytest.fixture
def users_by_user_groups(database, users, user_groups):
    with OpenBar():
        ubug_1 = model.UserByUserGroup.new(
            user_id=users["Active"]["id"],
            user_group_id=user_groups[0],
        )
        ubug_2 = model.UserByUserGroup.new(
            user_id=users["Inactive"]["id"],
            user_group_id=user_groups[1],
        )
        db.session.commit()
    return (ubug_1.id, ubug_2.id)


@pytest.fixture
def campaigns(database):
    with OpenBar():
        campaign_1 = model.Campaign.new(
            name="Campaign 1",
            start_time=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
        )
        campaign_2 = model.Campaign.new(
            name="Campaign 2",
            start_time=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
            end_time=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
        )
        db.session.commit()
    return campaign_1.id, campaign_2.id


@pytest.fixture
def campaign_scopes(database, campaigns):
    with OpenBar():
        cs_1 = model.CampaignScope.new(
            name="Campaign 1 - Scope 1",
            campaign_id=campaigns[0],
        )
        cs_2 = model.CampaignScope.new(
            name="Campaign 2 - Scope 1",
            campaign_id=campaigns[1],
        )
        db.session.commit()
    return (cs_1.id, cs_2.id)


@pytest.fixture
def user_groups_by_campaigns(database, user_groups, campaigns):
    with OpenBar():
        ugbc_1 = model.UserGroupByCampaign.new(
            user_group_id=user_groups[0],
            campaign_id=campaigns[0],
        )
        ugbc_2 = model.UserGroupByCampaign.new(
            user_group_id=user_groups[1],
            campaign_id=campaigns[1],
        )
        db.session.commit()
    return (ugbc_1.id, ugbc_2.id)


@pytest.fixture
def user_groups_by_campaign_scopes(database, user_groups, campaign_scopes):
    with OpenBar():
        ugbcs_1 = model.UserGroupByCampaignScope.new(
            user_group_id=user_groups[0],
            campaign_scope_id=campaign_scopes[0],
        )
        ugbcs_2 = model.UserGroupByCampaignScope.new(
            user_group_id=user_groups[1],
            campaign_scope_id=campaign_scopes[1],
        )
        db.session.commit()
    return (ugbcs_1.id, ugbcs_2.id)


@pytest.fixture
def timeseries_properties(database):
    with OpenBar():
        ts_p_1 = model.TimeseriesProperty.new(
            name="Min",
        )
        ts_p_2 = model.TimeseriesProperty.new(
            name="Max",
        )
        db.session.commit()
    return ts_p_1.id, ts_p_2.id


@pytest.fixture(params=[2])
def timeseries(request, database, campaigns, campaign_scopes):
    with OpenBar():
        ts_l = []
        for i in range(request.param):
            ts_i = model.Timeseries(
                name=f"Timeseries {i}",
                description=f"Test timeseries #{i}",
                campaign_id=campaigns[i % len(campaigns)],
                campaign_scope_id=campaign_scopes[i % len(campaign_scopes)],
            )
            ts_l.append(ts_i)
        db.session.add_all(ts_l)
        db.session.commit()
        return [ts.id for ts in ts_l]


@pytest.fixture
def timeseries_property_data(request, database, timeseries_properties, timeseries):
    with OpenBar():
        tspd_l = []
        for ts in timeseries:
            tspd_l.append(
                model.TimeseriesPropertyData(
                    timeseries_id=ts,
                    property_id=timeseries_properties[0],
                    value=12,
                )
            )
            tspd_l.append(
                model.TimeseriesPropertyData(
                    timeseries_id=ts,
                    property_id=timeseries_properties[1],
                    value=42,
                )
            )
        db.session.add_all(tspd_l)
        db.session.commit()
        return [tspd.id for tspd in tspd_l]


@pytest.fixture(params=[2])
def timeseries_by_data_states(request, database, timeseries):
    with OpenBar():
        ts_l = []
        for i in range(request.param):
            ts_i = model.TimeseriesByDataState(
                timeseries_id=timeseries[i % len(timeseries)],
                data_state_id=1,
            )
            ts_l.append(ts_i)
        db.session.add_all(ts_l)
        db.session.commit()
        return [ts.id for ts in ts_l]


@pytest.fixture(params=[4])
def timeseries_data(request, database, timeseries_by_data_states):
    with OpenBar():
        nb_tsd = request.param
        for tsbds_id in timeseries_by_data_states:
            start_dt = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
            for i in range(nb_tsd):
                timestamp = start_dt + dt.timedelta(hours=i)
                model.TimeseriesData.new(
                    timestamp=timestamp, timeseries_by_data_state_id=tsbds_id, value=i
                )
        db.session.commit()
    return (start_dt, start_dt + dt.timedelta(hours=nb_tsd))


@pytest.fixture
def events(database, campaigns, campaign_scopes):
    with OpenBar():
        tse_1 = model.Event.new(
            campaign_scope_id=campaign_scopes[0],
            timestamp=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
            source="Event source",
            category="observation_missing",
            level="INFO",
            state="NEW",
        )
        tse_2 = model.Event.new(
            campaign_scope_id=campaign_scopes[1],
            timestamp=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
            source="Another event source",
            category="observation_missing",
            level="WARNING",
            state="ONGOING",
        )
        db.session.commit()
    return (tse_1.id, tse_2.id)


@pytest.fixture
def sites(database, campaigns):
    with OpenBar():
        site_1 = model.Site.new(
            name="Site 1",
            campaign_id=campaigns[0],
        )
        site_2 = model.Site.new(
            name="Site 2",
            campaign_id=campaigns[1],
        )
        db.session.commit()
    return (site_1.id, site_2.id)


@pytest.fixture
def buildings(database, sites):
    with OpenBar():
        building_1 = model.Building.new(
            name="Building 1",
            site_id=sites[0],
        )
        building_2 = model.Building.new(
            name="Building 2",
            site_id=sites[1],
        )
        db.session.commit()
    return (building_1.id, building_2.id)


@pytest.fixture
def storeys(database, buildings):
    with OpenBar():
        storey_1 = model.Storey.new(
            name="Storey 1",
            building_id=buildings[0],
        )
        storey_2 = model.Storey.new(
            name="Storey 2",
            building_id=buildings[1],
        )
        db.session.commit()
    return (storey_1.id, storey_2.id)


@pytest.fixture
def spaces(database, storeys):
    with OpenBar():
        space_1 = model.Space.new(
            name="Space 1",
            storey_id=storeys[0],
        )
        space_2 = model.Space.new(
            name="Space 2",
            storey_id=storeys[1],
        )
        db.session.commit()
    return (space_1.id, space_2.id)


@pytest.fixture
def zones(database, campaigns):
    with OpenBar():
        zone_1 = model.Zone.new(
            name="Zone 1",
            campaign_id=campaigns[0],
        )
        zone_2 = model.Zone.new(
            name="Zone 2",
            campaign_id=campaigns[1],
        )
        db.session.commit()
    return (zone_1.id, zone_2.id)


@pytest.fixture
def structural_element_properties(database):
    with OpenBar():
        sep_1 = model.StructuralElementProperty.new(
            name="Surface",
        )
        sep_2 = model.StructuralElementProperty.new(
            name="Volume",
        )
        db.session.commit()
    return (sep_1.id, sep_2.id)


@pytest.fixture
def site_properties(database, structural_element_properties):
    with OpenBar():
        site_p_1 = model.SiteProperty.new(
            structural_element_property_id=structural_element_properties[0],
        )
        site_p_2 = model.SiteProperty.new(
            structural_element_property_id=structural_element_properties[1],
        )
        db.session.commit()
    return (site_p_1.id, site_p_2.id)


@pytest.fixture
def building_properties(database, structural_element_properties):
    with OpenBar():
        building_p_1 = model.BuildingProperty.new(
            structural_element_property_id=structural_element_properties[0],
        )
        building_p_2 = model.BuildingProperty.new(
            structural_element_property_id=structural_element_properties[1],
        )
        db.session.commit()
    return (building_p_1.id, building_p_2.id)


@pytest.fixture
def storey_properties(database, structural_element_properties):
    with OpenBar():
        storey_p_1 = model.StoreyProperty.new(
            structural_element_property_id=structural_element_properties[0],
        )
        storey_p_2 = model.StoreyProperty.new(
            structural_element_property_id=structural_element_properties[1],
        )
        db.session.commit()
    return (storey_p_1.id, storey_p_2.id)


@pytest.fixture
def space_properties(database, structural_element_properties):
    with OpenBar():
        space_p_1 = model.SpaceProperty.new(
            structural_element_property_id=structural_element_properties[0],
        )
        space_p_2 = model.SpaceProperty.new(
            structural_element_property_id=structural_element_properties[1],
        )
        db.session.commit()
    return (space_p_1.id, space_p_2.id)


@pytest.fixture
def zone_properties(database, structural_element_properties):
    with OpenBar():
        zone_p_1 = model.ZoneProperty.new(
            structural_element_property_id=structural_element_properties[0],
        )
        zone_p_2 = model.ZoneProperty.new(
            structural_element_property_id=structural_element_properties[1],
        )
        db.session.commit()
    return (zone_p_1.id, zone_p_2.id)


@pytest.fixture
def site_property_data(database, sites, site_properties):
    with OpenBar():
        spd_1 = model.SitePropertyData.new(
            site_id=sites[0],
            site_property_id=site_properties[0],
            value="12",
        )
        spd_2 = model.SitePropertyData.new(
            site_id=sites[1],
            site_property_id=site_properties[1],
            value="42",
        )
        db.session.commit()
    return (spd_1.id, spd_2.id)


@pytest.fixture
def building_property_data(database, sites, site_properties):
    with OpenBar():
        bpd_1 = model.BuildingPropertyData.new(
            building_id=sites[0],
            building_property_id=site_properties[0],
            value="12",
        )
        bpd_2 = model.BuildingPropertyData.new(
            building_id=sites[1],
            building_property_id=site_properties[1],
            value="42",
        )
        db.session.commit()
    return (bpd_1.id, bpd_2.id)


@pytest.fixture
def storey_property_data(database, storeys, storey_properties):
    with OpenBar():
        spd_1 = model.StoreyPropertyData.new(
            storey_id=storeys[0],
            storey_property_id=storey_properties[0],
            value="12",
        )
        spd_2 = model.StoreyPropertyData.new(
            storey_id=storeys[1],
            storey_property_id=storey_properties[1],
            value="42",
        )
        db.session.commit()
    return (spd_1.id, spd_2.id)


@pytest.fixture
def space_property_data(database, spaces, space_properties):
    with OpenBar():
        spd_1 = model.SpacePropertyData.new(
            space_id=spaces[0],
            space_property_id=space_properties[0],
            value="12",
        )
        spd_2 = model.SpacePropertyData.new(
            space_id=spaces[1],
            space_property_id=space_properties[1],
            value="42",
        )
        db.session.commit()
    return (spd_1.id, spd_2.id)


@pytest.fixture
def zone_property_data(database, zones, zone_properties):
    with OpenBar():
        zpd_1 = model.ZonePropertyData.new(
            zone_id=zones[0],
            zone_property_id=zone_properties[0],
            value="12",
        )
        zpd_2 = model.ZonePropertyData.new(
            zone_id=zones[1],
            zone_property_id=zone_properties[1],
            value="42",
        )
        db.session.commit()
    return (zpd_1.id, zpd_2.id)


@pytest.fixture
def timeseries_by_sites(database, sites, timeseries):
    with OpenBar():
        tbs_1 = model.TimeseriesBySite.new(
            site_id=sites[0],
            timeseries_id=timeseries[0],
        )
        tbs_2 = model.TimeseriesBySite.new(
            site_id=sites[1],
            timeseries_id=timeseries[1],
        )
        db.session.commit()
    return (tbs_1.id, tbs_2.id)


@pytest.fixture
def timeseries_by_buildings(database, buildings, timeseries):
    with OpenBar():
        tbb_1 = model.TimeseriesByBuilding.new(
            building_id=buildings[0],
            timeseries_id=timeseries[0],
        )
        tbb_2 = model.TimeseriesByBuilding.new(
            building_id=buildings[1],
            timeseries_id=timeseries[1],
        )
        db.session.commit()
    return (tbb_1.id, tbb_2.id)


@pytest.fixture
def timeseries_by_storeys(database, storeys, timeseries):
    with OpenBar():
        tbs_1 = model.TimeseriesByStorey.new(
            storey_id=storeys[0],
            timeseries_id=timeseries[0],
        )
        tbs_2 = model.TimeseriesByStorey.new(
            storey_id=storeys[1],
            timeseries_id=timeseries[1],
        )
        db.session.commit()
    return (tbs_1.id, tbs_2.id)


@pytest.fixture
def timeseries_by_spaces(database, spaces, timeseries):
    with OpenBar():
        tbs_1 = model.TimeseriesBySpace.new(
            space_id=spaces[0],
            timeseries_id=timeseries[0],
        )
        tbs_2 = model.TimeseriesBySpace.new(
            space_id=spaces[1],
            timeseries_id=timeseries[1],
        )
        db.session.commit()
    return (tbs_1.id, tbs_2.id)


@pytest.fixture
def timeseries_by_zones(database, spaces, timeseries):
    with OpenBar():
        tbz_1 = model.TimeseriesByZone.new(
            zone_id=spaces[0],
            timeseries_id=timeseries[0],
        )
        tbz_2 = model.TimeseriesByZone.new(
            zone_id=spaces[1],
            timeseries_id=timeseries[1],
        )
        db.session.commit()
    return (tbz_1.id, tbz_2.id)
