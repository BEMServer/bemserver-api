"""Energy consumption timeseries by sites resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EnergyConsumptionTimeseriesBySite

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EnergyConsumptionTimeseriesBySiteSchema,
    EnergyConsumptionTimeseriesBySiteQueryArgsSchema,
)


blp = Blueprint(
    "EnergyConsumptionTimeseriesBySite",
    __name__,
    url_prefix="/energy_consumption_timeseries_by_sites",
    description="Operations on energy consumption timeseries x site associations",
)


@blp.route("/")
class EnergyConsumptionTimeseriesBySiteViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyConsumptionTimeseriesBySiteQueryArgsSchema, location="query")
    @blp.response(200, EnergyConsumptionTimeseriesBySiteSchema(many=True))
    def get(self, args):
        """List energy consumption timeseries x site associations"""
        return EnergyConsumptionTimeseriesBySite.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyConsumptionTimeseriesBySiteSchema)
    @blp.response(201, EnergyConsumptionTimeseriesBySiteSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new energy consumption timeseries x site association"""
        item = EnergyConsumptionTimeseriesBySite.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EnergyConsumptionTimeseriesBySiteByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EnergyConsumptionTimeseriesBySiteSchema)
    def get(self, item_id):
        """Get energy consumption timeseries x site association ID"""
        item = EnergyConsumptionTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyConsumptionTimeseriesBySiteSchema)
    @blp.response(200, EnergyConsumptionTimeseriesBySiteSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing energy consumption timeseries x site association"""
        item = EnergyConsumptionTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EnergyConsumptionTimeseriesBySiteSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a energy consumption timeseries x site association"""
        item = EnergyConsumptionTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EnergyConsumptionTimeseriesBySiteSchema)
        item.delete()
        db.session.commit()
