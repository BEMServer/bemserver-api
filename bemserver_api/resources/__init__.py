"""Resources initialization"""

from . import timeseries
from . import timeseries_data
from . import events
from . import users
from . import campaigns


MODULES = (
    timeseries,
    timeseries_data,
    events,
    users,
    campaigns,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
