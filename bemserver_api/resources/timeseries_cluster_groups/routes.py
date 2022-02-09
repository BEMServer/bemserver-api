"""Timeseries cluster groups resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesClusterGroup

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import TimeseriesClusterGroupSchema, TimeseriesClusterGroupQueryArgsSchema


blp = Blueprint(
    "TimeseriesClusterGroup",
    __name__,
    url_prefix="/timeseries_cluster_groups",
    description="Operations on timeseries cluster groups x campaigns",
)


@blp.route("/")
class TimeseriesClusterGroupViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterGroupQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesClusterGroupSchema(many=True))
    def get(self, args):
        """List timeseries cluster groups"""
        return TimeseriesClusterGroup.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterGroupSchema)
    @blp.response(201, TimeseriesClusterGroupSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries cluster groups"""
        item = TimeseriesClusterGroup.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesClusterGroupByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesClusterGroupSchema)
    def get(self, item_id):
        """Get timeseries cluster groups by ID"""
        item = TimeseriesClusterGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterGroupSchema)
    @blp.response(200, TimeseriesClusterGroupSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries cluster group"""
        item = TimeseriesClusterGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesClusterGroupSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a timeseries cluster group"""
        item = TimeseriesClusterGroup.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
