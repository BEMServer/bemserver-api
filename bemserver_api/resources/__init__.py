"""Resources initialization"""

from . import users
from . import campaigns
from . import users_by_campaigns
from . import timeseries
from . import timeseries_groups
from . import timeseries_groups_by_users
from . import timeseries_groups_by_campaigns
from . import timeseries_data
from . import event_states
from . import event_levels
from . import event_categories
from . import event_channels
from . import event_channels_by_users
from . import event_channels_by_campaigns
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
    event_states,
    event_levels,
    event_categories,
    event_channels,
    event_channels_by_users,
    event_channels_by_campaigns,
    events,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
