"""Energy consumption resources"""
from flask_smorest import abort

from bemserver_core.process.energy_consumption import (
    compute_energy_consumption_breakdown_for_site,
    compute_energy_consumption_breakdown_for_building,
)
from bemserver_core.model import Site, Building


from bemserver_api import Blueprint

from .schemas import EnergyConsumptionSchema, EnergyConsumptionQueryArgsSchema


blp = Blueprint(
    "Energy consumption",
    __name__,
    url_prefix="/energy_consumption",
    description="Energy consumption operations",
)


@blp.route("/site/<int:site_id>")
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


@blp.route("/building/<int:building_id>")
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
