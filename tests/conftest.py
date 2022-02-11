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
            ret[name] = {"user": user, "creds": creds}
        db.session.commit()
        # Set id after commit
        for user in ret.values():
            user["id"] = user["user"].id
    return ret


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
def users_by_campaigns(campaigns, users):
    with OpenBar():
        user_by_campaign_1 = model.UserByCampaign.new(
            user_id=users["Active"]["id"],
            campaign_id=campaigns[0],
        )
        user_by_campaign_2 = model.UserByCampaign.new(
            user_id=users["Inactive"]["id"],
            campaign_id=campaigns[1],
        )
        db.session.commit()
    return user_by_campaign_1.id, user_by_campaign_2.id


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


@pytest.fixture
def timeseries_cluster_groups(database):
    with OpenBar():
        ts_group_1 = model.TimeseriesClusterGroup.new(
            name="TS Group 1",
        )
        ts_group_2 = model.TimeseriesClusterGroup.new(
            name="TS Group 2",
        )
        db.session.commit()
    return ts_group_1.id, ts_group_2.id


@pytest.fixture
def timeseries_cluster_groups_by_users(database, timeseries_cluster_groups, users):
    with OpenBar():
        tgbu_1 = model.TimeseriesClusterGroupByUser.new(
            timeseries_cluster_group_id=timeseries_cluster_groups[0],
            user_id=users["Active"]["id"],
        )
        tgbu_2 = model.TimeseriesClusterGroupByUser.new(
            timeseries_cluster_group_id=timeseries_cluster_groups[1],
            user_id=users["Inactive"]["id"],
        )
        db.session.commit()
    return tgbu_1.id, tgbu_2.id


@pytest.fixture(params=[2])
def timeseries_clusters(request, database, timeseries_cluster_groups):
    with OpenBar():
        tsc_l = []
        for i in range(request.param):
            tsc_i = model.TimeseriesCluster(
                name=f"Timeseries cluster {i}",
                description=f"Test timeseries cluster #{i}",
                group_id=timeseries_cluster_groups[i % len(timeseries_cluster_groups)],
            )
            tsc_l.append(tsc_i)
        db.session.add_all(tsc_l)
        db.session.commit()
        return [tsc.id for tsc in tsc_l]


@pytest.fixture(params=[2])
def timeseries(request, database, timeseries_clusters):
    with OpenBar():
        ts_l = []
        for i in range(request.param):
            ts_i = model.Timeseries(
                cluster_id=timeseries_clusters[i % len(timeseries_clusters)],
                data_state_id=1,
            )
            ts_l.append(ts_i)
        db.session.add_all(ts_l)
        db.session.commit()
        return [ts.id for ts in ts_l]


@pytest.fixture(params=[4])
def timeseries_data(request, database, timeseries):
    with OpenBar():
        nb_tsd = request.param
        for ts_id in timeseries:
            start_dt = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
            for i in range(nb_tsd):
                timestamp = start_dt + dt.timedelta(hours=i)
                model.TimeseriesData.new(
                    timestamp=timestamp, timeseries_id=ts_id, value=i
                )
        db.session.commit()
    return (start_dt, start_dt + dt.timedelta(hours=nb_tsd))


@pytest.fixture
def timeseries_cluster_groups_by_campaigns(timeseries_cluster_groups, campaigns):
    with OpenBar():
        ts_by_campaign_1 = model.TimeseriesClusterGroupByCampaign.new(
            timeseries_cluster_group_id=timeseries_cluster_groups[0],
            campaign_id=campaigns[0],
        )
        ts_by_campaign_2 = model.TimeseriesClusterGroupByCampaign.new(
            timeseries_cluster_group_id=timeseries_cluster_groups[1],
            campaign_id=campaigns[1],
        )
        db.session.commit()
    return ts_by_campaign_1.id, ts_by_campaign_2.id


@pytest.fixture
def event_channels(database):
    with OpenBar():
        event_channel_1 = model.EventChannel.new(
            name="Event channel 1",
        )
        event_channel_2 = model.EventChannel.new(
            name="Event channel 2",
        )
        db.session.commit()
    return event_channel_1.id, event_channel_2.id


@pytest.fixture
def event_channels_by_campaigns(database, campaigns, event_channels):
    with OpenBar():
        ecc_1 = model.EventChannelByCampaign.new(
            event_channel_id=event_channels[0],
            campaign_id=campaigns[0],
        )
        ecc_2 = model.EventChannelByCampaign.new(
            event_channel_id=event_channels[1],
            campaign_id=campaigns[1],
        )
        db.session.commit()
    return (ecc_1.id, ecc_2.id)


@pytest.fixture
def event_channels_by_users(database, event_channels, users):
    with OpenBar():
        ecbu_1 = model.EventChannelByUser.new(
            event_channel_id=event_channels[0],
            user_id=users["Active"]["id"],
        )
        ecbu_2 = model.EventChannelByUser.new(
            event_channel_id=event_channels[1],
            user_id=users["Inactive"]["id"],
        )
        db.session.commit()
    return ecbu_1.id, ecbu_2.id


@pytest.fixture
def events(database, campaigns, event_channels):
    with OpenBar():
        tse_1 = model.Event.new(
            channel_id=event_channels[0],
            timestamp=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
            source="Event source",
            category="observation_missing",
            level="INFO",
            state="NEW",
        )
        tse_2 = model.Event.new(
            channel_id=event_channels[1],
            timestamp=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
            source="Another event source",
            category="observation_missing",
            level="WARNING",
            state="ONGOING",
        )
        db.session.commit()
    return (tse_1.id, tse_2.id)
