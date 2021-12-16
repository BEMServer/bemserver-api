"""Resources initialization"""

from . import users
from . import campaigns
from . import users_by_campaigns
from . import timeseries
from . import timeseries_by_campaigns
from . import timeseries_data  # noqa
from . import events


MODULES = (
    users,
    campaigns,
    users_by_campaigns,
    timeseries,
    timeseries_by_campaigns,
    events,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
