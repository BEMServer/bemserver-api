"""Timeseries property data resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesPropertyData
from bemserver_core.exceptions import PropertyTypeInvalidError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesPropertyDataSchema,
    TimeseriesPropertyDataQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesPropertyData",
    __name__,
    url_prefix="/timeseries_property_data",
    description="Operations on timeseries property data",
)


@blp.route("/")
class TimeseriesPropertyDataViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesPropertyDataQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesPropertyDataSchema(many=True))
    def get(self, args):
        """List timeseries property data"""
        return TimeseriesPropertyData.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesPropertyDataSchema)
    @blp.response(201, TimeseriesPropertyDataSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries property data"""
        item = TimeseriesPropertyData.new(**new_item)
        try:
            db.session.commit()
        except PropertyTypeInvalidError:
            abort(422, errors={"json": {"value": ["Invalid type."]}})
        return item


@blp.route("/<int:item_id>")
class TimeseriesPropertyDataByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesPropertyDataSchema)
    def get(self, item_id):
        """Get timeseries property data by ID"""
        item = TimeseriesPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesPropertyDataSchema)
    @blp.response(200, TimeseriesPropertyDataSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries property data"""
        item = TimeseriesPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesPropertyDataSchema)
        item.update(**new_item)
        try:
            db.session.commit()
        except PropertyTypeInvalidError:
            abort(422, errors={"json": {"value": ["Invalid type."]}})
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries property data"""
        item = TimeseriesPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesPropertyDataSchema)
        item.delete()
        db.session.commit()
