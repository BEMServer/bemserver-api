"""Energy production timeseries by buildings resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EnergyProductionTimeseriesByBuilding

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EnergyProductionTimeseriesByBuildingSchema,
    EnergyProductionTimeseriesByBuildingQueryArgsSchema,
)


blp = Blueprint(
    "EnergyProductionTimeseriesByBuilding",
    __name__,
    url_prefix="/energy_production_timeseries_by_buildings",
    description="Operations on energy production timeseries x building associations",
)


@blp.route("/")
class EnergyProductionTimeseriesByBuildingViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(
        EnergyProductionTimeseriesByBuildingQueryArgsSchema, location="query"
    )
    @blp.response(200, EnergyProductionTimeseriesByBuildingSchema(many=True))
    def get(self, args):
        """List energy production timeseries x building associations"""
        return EnergyProductionTimeseriesByBuilding.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyProductionTimeseriesByBuildingSchema)
    @blp.response(201, EnergyProductionTimeseriesByBuildingSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new energy production timeseries x building association"""
        item = EnergyProductionTimeseriesByBuilding.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EnergyProductionTimeseriesByBuildingByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EnergyProductionTimeseriesByBuildingSchema)
    def get(self, item_id):
        """Get energy production timeseries x building association by ID"""
        item = EnergyProductionTimeseriesByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyProductionTimeseriesByBuildingSchema)
    @blp.response(200, EnergyProductionTimeseriesByBuildingSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing energy production timeseries x building association"""
        item = EnergyProductionTimeseriesByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EnergyProductionTimeseriesByBuildingSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a energy production timeseries x building association"""
        item = EnergyProductionTimeseriesByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EnergyProductionTimeseriesByBuildingSchema)
        item.delete()
        db.session.commit()
