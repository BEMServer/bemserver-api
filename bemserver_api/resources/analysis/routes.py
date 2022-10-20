"""Process resources"""
from flask_smorest import abort

from bemserver_core.process.completeness import compute_completeness
from bemserver_core.process.energy_consumption import (
    compute_energy_consumption_breakdown_for_site,
    compute_energy_consumption_breakdown_for_building,
)
from bemserver_core.model import Timeseries, TimeseriesDataState, Site, Building
from bemserver_core.exceptions import TimeseriesNotFoundError


from bemserver_api import Blueprint

from .schemas import (
    CompletenessSchema,
    CompletenessQueryArgsSchema,
    EnergyConsumptionSchema,
    EnergyConsumptionQueryArgsSchema,
)


blp = Blueprint(
    "Analysis", __name__, url_prefix="/analysis", description="Data analysis operations"
)


@blp.route("/completeness")
@blp.login_required
@blp.etag
@blp.arguments(CompletenessQueryArgsSchema, location="query")
@blp.response(200, CompletenessSchema)
def get_completeness(args):
    """Get timeseries data completeness

    Returns a report about data completeness, involving the number of values
    per time bucket and the sample interval.

    If the theoretical time interval for a timeseries is not defined in database,
    it is inferred from the maximum number of values per bucket.
    """
    try:
        timeseries = Timeseries.get_many_by_id(args["timeseries"])
    except TimeseriesNotFoundError as exc:
        abort(422, message=str(exc))
    if (data_state := TimeseriesDataState.get_by_id(args["data_state"])) is None:
        abort(422, errors={"query": {"data_state": "Unknown data state ID"}})

    completeness = compute_completeness(
        args["start_time"],
        args["end_time"],
        timeseries,
        data_state,
        args["bucket_width_value"],
        args["bucket_width_unit"],
        timezone=args["timezone"],
    )

    return completeness


@blp.route("/energy_consumption_for_site/<int:site_id>")
@blp.login_required
@blp.etag
@blp.arguments(EnergyConsumptionQueryArgsSchema, location="query")
@blp.response(200, EnergyConsumptionSchema)
def get_energy_consumption_breakdown_for_site(args, site_id):
    """Get energy consumption breakdown for a site"""
    site = Site.get_by_id(site_id)
    if site is None:
        abort(404)

    brkdwn = compute_energy_consumption_breakdown_for_site(
        site,
        args["start_time"],
        args["end_time"],
        args["bucket_width_value"],
        args["bucket_width_unit"],
        timezone=args["timezone"],
    )

    return brkdwn


@blp.route("/energy_consumption_for_building/<int:building_id>")
@blp.login_required
@blp.etag
@blp.arguments(EnergyConsumptionQueryArgsSchema, location="query")
@blp.response(200, EnergyConsumptionSchema)
def get_energy_consumption_breakdown_for_building(args, building_id):
    """Get energy consumption breakdown for a building"""
    building = Building.get_by_id(building_id)
    if building is None:
        abort(404)

    brkdwn = compute_energy_consumption_breakdown_for_building(
        building,
        args["start_time"],
        args["end_time"],
        args["bucket_width_value"],
        args["bucket_width_unit"],
        timezone=args["timezone"],
    )

    return brkdwn
