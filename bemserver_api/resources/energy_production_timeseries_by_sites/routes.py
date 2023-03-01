"""Energy production timeseries by sites resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EnergyProductionTimeseriesBySite

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EnergyProductionTimeseriesBySiteSchema,
    EnergyProductionTimeseriesBySiteQueryArgsSchema,
)


blp = Blueprint(
    "EnergyProductionTimeseriesBySite",
    __name__,
    url_prefix="/energy_production_timeseries_by_sites",
    description="Operations on energy production timeseries x site associations",
)


@blp.route("/")
class EnergyProductionTimeseriesBySiteViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyProductionTimeseriesBySiteQueryArgsSchema, location="query")
    @blp.response(200, EnergyProductionTimeseriesBySiteSchema(many=True))
    def get(self, args):
        """List energy production timeseries x site associations"""
        return EnergyProductionTimeseriesBySite.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyProductionTimeseriesBySiteSchema)
    @blp.response(201, EnergyProductionTimeseriesBySiteSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new energy production timeseries x site association"""
        item = EnergyProductionTimeseriesBySite.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EnergyProductionTimeseriesBySiteByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EnergyProductionTimeseriesBySiteSchema)
    def get(self, item_id):
        """Get energy production timeseries x site association by ID"""
        item = EnergyProductionTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(EnergyProductionTimeseriesBySiteSchema)
    @blp.response(200, EnergyProductionTimeseriesBySiteSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing energy production timeseries x site association"""
        item = EnergyProductionTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EnergyProductionTimeseriesBySiteSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a energy production timeseries x site association"""
        item = EnergyProductionTimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EnergyProductionTimeseriesBySiteSchema)
        item.delete()
        db.session.commit()
