"""Resources initialization"""

from . import about
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
from . import event_categories
from . import events
from . import timeseries_by_events
from . import events_by_sites
from . import events_by_buildings
from . import events_by_storeys
from . import events_by_spaces
from . import events_by_zones
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
from . import energy_sources
from . import energy_end_uses
from . import energy_consumption_timeseries_by_sites
from . import energy_consumption_timeseries_by_buildings
from . import input_output
from . import analysis
from . import st_cleanups_by_campaigns
from . import st_cleanups_by_timeseries
from . import st_check_missings_by_campaigns


MODULES = (
    about,
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
    event_categories,
    events,
    timeseries_by_events,
    events_by_sites,
    events_by_buildings,
    events_by_storeys,
    events_by_spaces,
    events_by_zones,
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
    energy_sources,
    energy_end_uses,
    energy_consumption_timeseries_by_sites,
    energy_consumption_timeseries_by_buildings,
    input_output,
    analysis,
    st_cleanups_by_campaigns,
    st_cleanups_by_timeseries,
    st_check_missings_by_campaigns,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
