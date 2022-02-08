"""Timeseries cluster groups by users resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesClusterGroupByUser

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesClusterGroupByUserSchema,
    TimeseriesClusterGroupByUserQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesClusterGroupByUser",
    __name__,
    url_prefix="/timeseries_cluster_groups_by_users",
    description="Operations on timeseries cluster groups x users associations",
)


@blp.route("/")
class TimeseriesClusterGroupByUserViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterGroupByUserQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesClusterGroupByUserSchema(many=True))
    def get(self, args):
        """List user x timeseries cluster groups associations"""
        return TimeseriesClusterGroupByUser.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterGroupByUserSchema)
    @blp.response(201, TimeseriesClusterGroupByUserSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new user x timeseries cluster groups association"""
        item = TimeseriesClusterGroupByUser.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesClusterGroupByUserByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesClusterGroupByUserSchema)
    def get(self, item_id):
        """Get user x timeseries cluster groups association by ID"""
        item = TimeseriesClusterGroupByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a user x timeseries cluster groups association"""
        item = TimeseriesClusterGroupByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
