"""TimeseriesEvents resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import TimeseriesEvent

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    TimeseriesEventSchema,
    TimeseriesEventPutSchema,
    TimeseriesEventQueryArgsSchema,
)


blp = Blueprint(
    "Timeseries events",
    __name__,
    url_prefix="/events/timeseries",
    description="Operations on timeseries data",
)


@blp.route("/")
class TimeseriesEventsViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesEventQueryArgsSchema, location="query")
    @blp.response(200, TimeseriesEventSchema(many=True))
    @blp.paginate(SQLCursorPage)
    # TODO: kwargs?
    def get(self, args):
        """List events"""
        return TimeseriesEvent.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesEventSchema)
    @blp.response(201, TimeseriesEventSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event"""
        item = TimeseriesEvent.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class TimeseriesEventsByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, TimeseriesEventSchema)
    def get(self, item_id):
        """Get en event by its ID"""
        item = TimeseriesEvent.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(TimeseriesEventPutSchema)
    @blp.response(200, TimeseriesEventSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries"""
        item = TimeseriesEvent.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesEventSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event"""
        item = TimeseriesEvent.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, TimeseriesEventSchema)
        item.delete()
        db.session.commit()
