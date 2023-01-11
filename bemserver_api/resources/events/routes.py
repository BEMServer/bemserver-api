"""Events resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Event

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import EventSchema, EventPutSchema, EventQueryArgsSchema


blp = Blueprint(
    "Event", __name__, url_prefix="/events", description="Operations on events"
)


@blp.route("/")
class EventsViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventQueryArgsSchema, location="query")
    @blp.response(200, EventSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List events"""
        return Event.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventSchema)
    @blp.response(201, EventSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event"""
        item = Event.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EventsByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventSchema)
    def get(self, item_id):
        """Get event by ID"""
        item = Event.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(EventPutSchema)
    @blp.response(200, EventSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing event"""
        item = Event.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EventSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event"""
        item = Event.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EventSchema)
        item.delete()
        db.session.commit()
