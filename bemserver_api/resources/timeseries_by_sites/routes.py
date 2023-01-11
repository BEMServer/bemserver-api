"""Timeseries by sites resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesBySite

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    TimeseriesBySiteSchema,
    TimeseriesBySiteQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesBySite",
    __name__,
    url_prefix="/timeseries_by_sites",
    description="Operations on timeseries x site associations",
)


@blp.route("/")
class TimeseriesBySiteViews(MethodView):
    @blp.login_required
    @blp.arguments(TimeseriesBySiteQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesBySiteSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List timeseries x site associations"""
        return TimeseriesBySite.get(**args)

    @blp.login_required
    @blp.arguments(TimeseriesBySiteSchema)
    @blp.response(201, TimeseriesBySiteSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries x site association"""
        item = TimeseriesBySite.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesBySiteByIdViews(MethodView):
    @blp.login_required
    @blp.response(200, TimeseriesBySiteSchema)
    def get(self, item_id):
        """Get timeseries x site association by ID"""
        item = TimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries x site association"""
        item = TimeseriesBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
