"""Resources initialization"""

from . import timeseries
from . import timeseries_data
from . import events
from . import users
from . import campaigns
from . import users_by_campaigns
from . import timeseries_by_campaigns


MODULES = (
    timeseries,
    timeseries_data,
    events,
    users,
    campaigns,
    users_by_campaigns,
    timeseries_by_campaigns,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
