"""Energy consumption timeseries by buildings resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EnergyConsumptionTimeseriesByBuilding

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EnergyConsumptionTimeseriesByBuildingSchema,
    EnergyConsumptionTimeseriesByBuildingQueryArgsSchema,
)


blp = Blueprint(
    "EnergyConsumptionTimeseriesByBuilding",
    __name__,
    url_prefix="/energy_consumption_timeseries_by_buildings",
    description="Operations on energy consumption timeseries x building associations",
)


@blp.route("/")
class EnergyConsumptionTimeseriesByBuildingViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(
        EnergyConsumptionTimeseriesByBuildingQueryArgsSchema, location="query"
    )
    @blp.response(200, EnergyConsumptionTimeseriesByBuildingSchema(many=True))
    def get(self, args):
        """List energy consumption timeseries x building associations"""
        return EnergyConsumptionTimeseriesByBuilding.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyConsumptionTimeseriesByBuildingSchema)
    @blp.response(201, EnergyConsumptionTimeseriesByBuildingSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new energy consumption timeseries x building association"""
        item = EnergyConsumptionTimeseriesByBuilding.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EnergyConsumptionTimeseriesByBuildingByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EnergyConsumptionTimeseriesByBuildingSchema)
    def get(self, item_id):
        """Get energy consumption timeseries x building association ID"""
        item = EnergyConsumptionTimeseriesByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyConsumptionTimeseriesByBuildingSchema)
    @blp.response(200, EnergyConsumptionTimeseriesByBuildingSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing energy consumption timeseries x building association"""
        item = EnergyConsumptionTimeseriesByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EnergyConsumptionTimeseriesByBuildingSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a energy consumption timeseries x building association"""
        item = EnergyConsumptionTimeseriesByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EnergyConsumptionTimeseriesByBuildingSchema)
        item.delete()
        db.session.commit()
