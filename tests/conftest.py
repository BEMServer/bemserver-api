"""Global conftest"""
import base64
import datetime as dt

import flask.testing

from bemserver_core.database import db
from bemserver_core.authorization import CurrentUser, OpenBar
from bemserver_core import model
from bemserver_core.testutils import setup_db

import pytest
from pytest_postgresql import factories as ppf

from bemserver_api import create_app

from tests.common import TestConfig, AUTH_HEADER


postgresql_proc = ppf.postgresql_proc(
    postgres_options="-c shared_preload_libraries='timescaledb'"
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


with OpenBar():
    AdminUser = CurrentUser(
        model.User(name="Chuck", email="chuck@test.com", is_admin=True, is_active=True)
    )


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
    with AdminUser:
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
    with AdminUser:
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


@pytest.fixture(params=[2])
def timeseries(request, database):
    ts_l = []
    for i in range(request.param):
        ts_i = model.Timeseries(
            name=f"Timeseries {i}",
            description=f"Test timeseries #{i}",
        )
        ts_l.append(ts_i)
    db.session.add_all(ts_l)
    db.session.commit()
    return [ts.id for ts in ts_l]


@pytest.fixture(params=[4])
def timeseries_data(request, database, timeseries):
    nb_tsd = request.param
    with AdminUser:
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
def timeseries_by_campaigns(timeseries, campaigns):
    with AdminUser:
        ts_by_campaign_1 = model.TimeseriesByCampaign.new(
            timeseries_id=timeseries[0],
            campaign_id=campaigns[0],
        )
        ts_by_campaign_2 = model.TimeseriesByCampaign.new(
            timeseries_id=timeseries[1],
            campaign_id=campaigns[1],
        )
        db.session.commit()
    return ts_by_campaign_1.id, ts_by_campaign_2.id


@pytest.fixture
def event_channels(database):
    with AdminUser:
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
        ecc_1 = model.EventChannelByCampaign(
            event_channel_id=event_channels[0],
            campaign_id=campaigns[0],
        )
        db.session.add(ecc_1)
        ecc_2 = model.EventChannelByCampaign(
            event_channel_id=event_channels[1],
            campaign_id=campaigns[1],
        )
        db.session.add(ecc_2)
        db.session.commit()
    return (ecc_1.id, ecc_2.id)


@pytest.fixture
def timeseries_events_by_campaigns(database, campaigns, event_channels):
    with OpenBar():
        tse_1 = model.TimeseriesEvent(
            channel_id=event_channels[0],
            timestamp=dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc),
            source="Event source",
            category="observation_missing",
            level="INFO",
            state="NEW",
        )
        db.session.add(tse_1)
        tse_2 = model.TimeseriesEvent(
            channel_id=event_channels[1],
            timestamp=dt.datetime(2021, 1, 1, tzinfo=dt.timezone.utc),
            source="Another event source",
            category="observation_missing",
            level="WARNING",
            state="ONGOING",
        )
        db.session.add(tse_2)
        db.session.commit()
    return (tse_1.id, tse_2.id)
