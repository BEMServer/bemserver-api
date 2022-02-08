"""Timeseries clusters resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesCluster

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import TimeseriesClusterSchema, TimeseriesClusterQueryArgsSchema


blp = Blueprint(
    "TimeseriesCluster",
    __name__,
    url_prefix="/timeseries_clusters",
    description="Operations on timeseries clusters",
)


@blp.route("/")
class TimeseriesClusterViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesClusterSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List timeseries clusters"""
        return TimeseriesCluster.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterSchema)
    @blp.response(201, TimeseriesClusterSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries cluster"""
        item = TimeseriesCluster.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesClusterByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesClusterSchema)
    def get(self, item_id):
        """Get timeseries cluster by ID"""
        item = TimeseriesCluster.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterSchema)
    @blp.response(200, TimeseriesClusterSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries cluster"""
        item = TimeseriesCluster.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesClusterSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a timeseries cluster"""
        item = TimeseriesCluster.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesClusterSchema)
        item.delete()
        db.session.commit()
