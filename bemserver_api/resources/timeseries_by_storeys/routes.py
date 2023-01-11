"""Timeseries by storeys resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesByStorey

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    TimeseriesByStoreySchema,
    TimeseriesByStoreyQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesByStorey",
    __name__,
    url_prefix="/timeseries_by_storeys",
    description="Operations on timeseries x storey associations",
)


@blp.route("/")
class TimeseriesByStoreyViews(MethodView):
    @blp.login_required
    @blp.arguments(TimeseriesByStoreyQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesByStoreySchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List timeseries x storey associations"""
        return TimeseriesByStorey.get(**args)

    @blp.login_required
    @blp.arguments(TimeseriesByStoreySchema)
    @blp.response(201, TimeseriesByStoreySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries x storey association"""
        item = TimeseriesByStorey.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesByStoreyByIdViews(MethodView):
    @blp.login_required
    @blp.response(200, TimeseriesByStoreySchema)
    def get(self, item_id):
        """Get timeseries x storey association by ID"""
        item = TimeseriesByStorey.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries x storey association"""
        item = TimeseriesByStorey.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
