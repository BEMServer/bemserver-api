"""Timeseries groups resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesGroup

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import TimeseriesGroupSchema, TimeseriesGroupQueryArgsSchema


blp = Blueprint(
    "TimeseriesGroup",
    __name__,
    url_prefix="/timeseries_groups",
    description="Operations on timeseries groups x campaigns",
)


@blp.route("/")
class TimeseriesGroupViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesGroupQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesGroupSchema(many=True))
    def get(self, args):
        """List timeseries groups"""
        return TimeseriesGroup.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesGroupSchema)
    @blp.response(201, TimeseriesGroupSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries groups"""
        item = TimeseriesGroup.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesGroupByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesGroupSchema)
    def get(self, item_id):
        """Get timeseries groups by ID"""
        item = TimeseriesGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesGroupSchema)
    @blp.response(200, TimeseriesGroupSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries"""
        item = TimeseriesGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesGroupSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a timeseries groups"""
        item = TimeseriesGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
