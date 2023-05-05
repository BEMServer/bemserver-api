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
from . import event_categories_by_users
from . import timeseries_by_events
from . import events_by_sites
from . import events_by_buildings
from . import events_by_storeys
from . import events_by_spaces
from . import events_by_zones
from . import notifications
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
from . import energies
from . import energy_end_uses
from . import energy_production_technologies
from . import energy_consumption_timeseries_by_sites
from . import energy_consumption_timeseries_by_buildings
from . import energy_production_timeseries_by_sites
from . import energy_production_timeseries_by_buildings
from . import weather_timeseries_by_sites
from . import input_output
from . import analysis
from . import st_cleanups_by_campaigns
from . import st_cleanups_by_timeseries
from . import st_check_missings_by_campaigns
from . import st_check_outliers_by_campaigns
from . import st_download_weather_data_by_sites
from . import st_download_weather_forecast_data_by_sites


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
    event_categories_by_users,
    events,
    timeseries_by_events,
    events_by_sites,
    events_by_buildings,
    events_by_storeys,
    events_by_spaces,
    events_by_zones,
    notifications,
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
    energies,
    energy_end_uses,
    energy_production_technologies,
    energy_consumption_timeseries_by_sites,
    energy_consumption_timeseries_by_buildings,
    energy_production_timeseries_by_sites,
    energy_production_timeseries_by_buildings,
    weather_timeseries_by_sites,
    input_output,
    analysis,
    st_cleanups_by_campaigns,
    st_cleanups_by_timeseries,
    st_check_missings_by_campaigns,
    st_check_outliers_by_campaigns,
    st_download_weather_data_by_sites,
    st_download_weather_forecast_data_by_sites,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
