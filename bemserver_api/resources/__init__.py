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
from . import zones
from . import structural_element_properties
from . import site_properties
from . import building_properties
from . import storey_properties
from . import space_properties
from . import zone_properties
from . import site_property_data
from . import building_property_data
from . import storey_property_data
from . import space_property_data
from . import zone_property_data
from . import timeseries_by_sites
from . import timeseries_by_buildings
from . import timeseries_by_storeys
from . import timeseries_by_spaces
from . import timeseries_by_zones
from . import input_output


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
    zones,
    structural_element_properties,
    site_properties,
    building_properties,
    storey_properties,
    space_properties,
    zone_properties,
    site_property_data,
    building_property_data,
    storey_property_data,
    space_property_data,
    zone_property_data,
    timeseries_by_sites,
    timeseries_by_buildings,
    timeseries_by_storeys,
    timeseries_by_spaces,
    timeseries_by_zones,
    input_output,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
