"""Resources initialization"""

from . import users
from . import campaigns
from . import users_by_campaigns
from . import timeseries
from . import timeseries_groups
from . import timeseries_groups_by_users
from . import timeseries_groups_by_campaigns
from . import timeseries_data
from . import events


MODULES = (
    users,
    campaigns,
    users_by_campaigns,
    timeseries,
    timeseries_groups,
    timeseries_groups_by_users,
    timeseries_groups_by_campaigns,
    timeseries_data,
    events,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
