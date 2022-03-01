"""Timeseries groups by users resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesGroupByUser

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    TimeseriesGroupByUserSchema,
    TimeseriesGroupByUserQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesGroupByUser",
    __name__,
    url_prefix="/timeseries_groups_by_users",
    description="Operations on timeseries groups x users associations",
)


@blp.route("/")
class TimeseriesGroupByUserViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesGroupByUserQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesGroupByUserSchema(many=True))
    def get(self, args):
        """List user x timeseries groups associations"""
        return TimeseriesGroupByUser.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesGroupByUserSchema)
    @blp.response(201, TimeseriesGroupByUserSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new user x timeseries groups association"""
        item = TimeseriesGroupByUser.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesGroupByUserByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesGroupByUserSchema)
    def get(self, item_id):
        """Get user x timeseries groups association by ID"""
        item = TimeseriesGroupByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a user x timeseries groups association"""
        item = TimeseriesGroupByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
