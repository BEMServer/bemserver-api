"""Timeseries by zones resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesByZone

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesByZoneSchema,
    TimeseriesByZoneQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesByZone",
    __name__,
    url_prefix="/timeseries_by_zones",
    description="Operations on timeseries x zone associations",
)


@blp.route("/")
class TimeseriesByZoneViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesByZoneQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesByZoneSchema(many=True))
    def get(self, args):
        """List timeseries x zone associations"""
        return TimeseriesByZone.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesByZoneSchema)
    @blp.response(201, TimeseriesByZoneSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries x zone association"""
        item = TimeseriesByZone.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesByZoneByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesByZoneSchema)
    def get(self, item_id):
        """Get timeseries x zone association ID"""
        item = TimeseriesByZone.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesByZoneSchema)
    @blp.response(200, TimeseriesByZoneSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries x zone association"""
        item = TimeseriesByZone.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesByZoneSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries x zone association"""
        item = TimeseriesByZone.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesByZoneSchema)
        item.delete()
        db.session.commit()
