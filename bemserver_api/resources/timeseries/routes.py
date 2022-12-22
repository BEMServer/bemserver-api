"""Timeseries resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Timeseries

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    TimeseriesSchema,
    TimeseriesPutSchema,
    TimeseriesQueryArgsSchema,
    TimeseriesRecurseArgsSchema,
)


blp = Blueprint(
    "Timeseries",
    __name__,
    url_prefix="/timeseries",
    description="Operations on timeseries",
)


@blp.route("/")
class TimeseriesViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List timeseries"""
        return Timeseries.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesSchema)
    @blp.response(201, TimeseriesSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new timeseries"""
        item = Timeseries.new(**new_item)
        db.session.commit()
        return item


@blp.route("/by_site/<int:item_id>")
@blp.login_required
@blp.etag
@blp.arguments(TimeseriesRecurseArgsSchema, location="query")
@blp.response(200, TimeseriesSchema(many=True))
@blp.paginate(SQLCursorPage)
def get_by_site(args, item_id):
    """Get timeseries for a given site"""
    return Timeseries.get_by_site(item_id, **args)


@blp.route("/by_building/<int:item_id>")
@blp.login_required
@blp.etag
@blp.arguments(TimeseriesRecurseArgsSchema, location="query")
@blp.response(200, TimeseriesSchema(many=True))
@blp.paginate(SQLCursorPage)
def get_by_building(args, item_id):
    """Get timeseries for a given building"""
    return Timeseries.get_by_building(item_id, **args)


@blp.route("/by_storey/<int:item_id>")
@blp.login_required
@blp.etag
@blp.arguments(TimeseriesRecurseArgsSchema, location="query")
@blp.response(200, TimeseriesSchema(many=True))
@blp.paginate(SQLCursorPage)
def get_by_storey(args, item_id):
    """Get timeseries for a given storey"""
    return Timeseries.get_by_storey(item_id, **args)


@blp.route("/by_space/<int:item_id>")
@blp.login_required
@blp.etag
@blp.response(200, TimeseriesSchema(many=True))
@blp.paginate(SQLCursorPage)
def get_by_space(item_id):
    """Get timeseries for a given space"""
    return Timeseries.get_by_space(item_id)


@blp.route("/by_zone/<int:item_id>")
@blp.login_required
@blp.etag
@blp.response(200, TimeseriesSchema(many=True))
@blp.paginate(SQLCursorPage)
def get_by_zone(item_id):
    """Get timeseries for a given zone"""
    return Timeseries.get_by_zone(item_id)


@blp.route("/by_event/<int:item_id>")
@blp.login_required
@blp.etag
@blp.response(200, TimeseriesSchema(many=True))
@blp.paginate(SQLCursorPage)
def get_by_event(item_id):
    """Get timeseries for a given event"""
    return Timeseries.get_by_event(item_id)


@blp.route("/<int:item_id>")
class TimeseriesByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesSchema)
    def get(self, item_id):
        """Get timeseries by ID"""
        item = Timeseries.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesPutSchema)
    @blp.response(200, TimeseriesSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries"""
        item = Timeseries.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a timeseries"""
        item = Timeseries.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesSchema)
        item.delete()
        db.session.commit()
