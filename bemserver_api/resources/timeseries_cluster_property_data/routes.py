"""Timeseries cluster property data resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesClusterPropertyData

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesClusterPropertyDataSchema,
    TimeseriesClusterPropertyDataQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesClusterPropertyData",
    __name__,
    url_prefix="/timeseries_cluster_property_data",
    description="Operations on timeseries property data",
)


@blp.route("/")
class TimeseriesClusterPropertyDataViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterPropertyDataQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesClusterPropertyDataSchema(many=True))
    def get(self, args):
        """List timeseries cluster property data"""
        return TimeseriesClusterPropertyData.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterPropertyDataSchema)
    @blp.response(201, TimeseriesClusterPropertyDataSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries cluster property data"""
        item = TimeseriesClusterPropertyData.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesClusterPropertyDataByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesClusterPropertyDataSchema)
    def get(self, item_id):
        """Get timeseries cluster property data by ID"""
        item = TimeseriesClusterPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesClusterPropertyDataSchema)
    @blp.response(200, TimeseriesClusterPropertyDataSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries property data"""
        item = TimeseriesClusterPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesClusterPropertyDataSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a timeseries cluster property data"""
        item = TimeseriesClusterPropertyData.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
