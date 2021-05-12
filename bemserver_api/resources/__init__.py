"""Resources initialization"""

from . import timeseries
from . import timeseries_data
from . import events


MODULES = (
    timeseries,
    timeseries_data,
    events,
)


def register_blueprints(api):
    """Initialize application with all modules"""
    for module in MODULES:
        module.register_blueprints(api)
