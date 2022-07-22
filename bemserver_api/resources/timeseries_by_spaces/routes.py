"""Timeseries by spaces resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesBySpace

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesBySpaceSchema,
    TimeseriesBySpaceQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesBySpace",
    __name__,
    url_prefix="/timeseries_by_spaces",
    description="Operations on timeseries x space associations",
)


@blp.route("/")
class TimeseriesBySpaceViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesBySpaceQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesBySpaceSchema(many=True))
    def get(self, args):
        """List timeseries x space associations"""
        return TimeseriesBySpace.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesBySpaceSchema)
    @blp.response(201, TimeseriesBySpaceSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries x space association"""
        item = TimeseriesBySpace.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesBySpaceByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesBySpaceSchema)
    def get(self, item_id):
        """Get timeseries x space association ID"""
        item = TimeseriesBySpace.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesBySpaceSchema)
    @blp.response(200, TimeseriesBySpaceSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries x space association"""
        item = TimeseriesBySpace.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesBySpaceSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries x space association"""
        item = TimeseriesBySpace.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesBySpaceSchema)
        item.delete()
        db.session.commit()
