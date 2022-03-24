"""Resources initialization"""

from . import users
from . import user_groups
from . import users_by_user_groups
from . import campaigns
from . import user_groups_by_campaigns
from . import campaign_scopes
from . import user_groups_by_campaign_scopes
from . import timeseries_properties
from . import timeseries_data_states
from . import timeseries
from . import timeseries_property_data
from . import timeseries_data
from . import event_states
from . import event_levels
from . import event_categories
from . import events
from . import sites
from . import buildings
from . import storeys
from . import spaces
from . import structural_element_properties
from . import site_properties
from . import building_properties


MODULES = (
    users,
    user_groups,
    users_by_user_groups,
    campaigns,
    user_groups_by_campaigns,
    campaign_scopes,
    user_groups_by_campaign_scopes,
    timeseries_properties,
    timeseries_data_states,
    timeseries,
    timeseries_property_data,
    timeseries_data,
    event_states,
    event_levels,
    event_categories,
    events,
    sites,
    buildings,
    storeys,
    spaces,
    structural_element_properties,
    site_properties,
    building_properties,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
