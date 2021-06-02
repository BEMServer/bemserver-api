"""Global conftest"""
import base64
import datetime as dt

from bemserver_core.database import db
from bemserver_core import model
from bemserver_core.testutils import setup_db

import pytest
from pytest_postgresql import factories as ppf

from bemserver_api import create_app

from tests.common import TestConfig


postgresql_proc = ppf.postgresql_proc(
    postgres_options="-c shared_preload_libraries='timescaledb'"
)
postgresql = ppf.postgresql('postgresql_proc')


@pytest.fixture
def database(postgresql):
    yield from setup_db(postgresql)


@pytest.fixture(params=(TestConfig, ))
def app(request, database):

    class AppConfig(request.param):
        SQLALCHEMY_DATABASE_URI = database.url

    application = create_app(AppConfig)
    yield application


USERS = (
    ("Chuck", "N0rris", "chuck@test.com", True, True),
    ("Active", "@ctive", "active@test.com", False, True),
    ("Inactive", "in@ctive", "inactive@test.com", False, False),
)


@pytest.fixture(params=(USERS, ))
def users(database, request):
    ret = {}
    for user in request.param:
        name, password, email, is_admin, is_active = user
        user = model.User(
            name=name,
            email=email,
            is_admin=is_admin,
            is_active=is_active
        )
        user.set_password(password)
        creds = base64.b64encode(f"{email}:{password}".encode()).decode()
        db.session.add(user)
        db.session.commit()
        ret[name] = {"id": user.id, "creds": creds}
    return ret


@pytest.fixture
def campaigns(database):
    campaign_1 = model.Campaign(
        name="Campaign 1",
    )
    campaign_2 = model.Campaign(
        name="Campaign 2",
    )
    db.session.add(campaign_1)
    db.session.add(campaign_2)
    db.session.commit()
    return campaign_1.id, campaign_2.id


@pytest.fixture(params=[{}])
def timeseries_data(request, database):

    param = request.param

    nb_ts = param.get("nb_ts", 1)
    nb_tsd = param.get("nb_tsd", 24 * 100)

    ts_l = []

    for i in range(nb_ts):
        ts_i = model.Timeseries(
            name=f"Timeseries {i}",
            description=f"Test timeseries #{i}",
        )
        db.session.add(ts_i)

        start_dt = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)
        for i in range(nb_tsd):
            timestamp = start_dt + dt.timedelta(hours=i)
            db.session.add(
                model.TimeseriesData(
                    timestamp=timestamp,
                    timeseries=ts_i,
                    value=i
                )
            )

        ts_l.append(ts_i)

    db.session.commit()

    return [
        (ts.id, nb_tsd, start_dt, start_dt + dt.timedelta(hours=nb_tsd))
        for ts in ts_l
    ]
