"""Timeseries by buildings resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesByBuilding

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    TimeseriesByBuildingSchema,
    TimeseriesByBuildingQueryArgsSchema,
)


blp = Blueprint(
    "TimeseriesByBuilding",
    __name__,
    url_prefix="/timeseries_by_buildings",
    description="Operations on timeseries x building associations",
)


@blp.route("/")
class TimeseriesByBuildingViews(MethodView):
    @blp.login_required
    @blp.arguments(TimeseriesByBuildingQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesByBuildingSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List timeseries x building associations"""
        return TimeseriesByBuilding.get(**args)

    @blp.login_required
    @blp.arguments(TimeseriesByBuildingSchema)
    @blp.response(201, TimeseriesByBuildingSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries x building association"""
        item = TimeseriesByBuilding.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesByBuildingByIdViews(MethodView):
    @blp.login_required
    @blp.response(200, TimeseriesByBuildingSchema)
    def get(self, item_id):
        """Get timeseries x building association by ID"""
        item = TimeseriesByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries x building association"""
        item = TimeseriesByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
