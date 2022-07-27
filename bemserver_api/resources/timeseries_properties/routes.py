"""Timeseries properties resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesProperty

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesPropertySchema,
    TimeseriesPropertyPutSchema,
    TimeseriesPropertyQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesProperty",
    __name__,
    url_prefix="/timeseries_properties",
    description="Operations on timeseries properties",
)


@blp.route("/")
class TimeseriesPropertiesViews(MethodView):
    @blp.login_required
    @blp.arguments(TimeseriesPropertyQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesPropertySchema(many=True))
    def get(self, args):
        """List timeseries properties"""
        return TimeseriesProperty.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesPropertySchema)
    @blp.response(201, TimeseriesPropertySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries property"""
        item = TimeseriesProperty.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesPropertyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesPropertySchema)
    def get(self, item_id):
        """Get timeseries property by ID"""
        item = TimeseriesProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesPropertyPutSchema)
    @blp.response(200, TimeseriesPropertySchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries property"""
        item = TimeseriesProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesPropertySchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries property"""
        item = TimeseriesProperty.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesPropertySchema)
        item.delete()
        db.session.commit()
