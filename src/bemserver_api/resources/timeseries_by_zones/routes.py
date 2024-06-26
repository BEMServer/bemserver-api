"""Timeseries by zones resources"""

from flask.views import MethodView

from flask_smorest import abort

from bemserver_core.model import TimeseriesByZone

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    TimeseriesByZoneQueryArgsSchema,
    TimeseriesByZoneSchema,
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
    @blp.arguments(TimeseriesByZoneQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesByZoneSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List timeseries x zone associations"""
        return TimeseriesByZone.get(**args)

    @blp.login_required
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
    @blp.response(200, TimeseriesByZoneSchema)
    def get(self, item_id):
        """Get timeseries x zone association by ID"""
        item = TimeseriesByZone.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries x zone association"""
        item = TimeseriesByZone.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
