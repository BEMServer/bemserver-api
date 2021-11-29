"""Events resources"""

from flask.views import MethodView
from flask_smorest import abort
from flask_smorest.error_handler import ErrorSchema

from bemserver_core.model import (
    EventState, EventCategory, EventLevel, EventTarget, Event)
from bemserver_core.model.exceptions import EventError

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    EventStateSchema, EventCategorySchema, EventLevelSchema, EventTargetSchema,
    EventSchema, EventQueryArgsSchema,
    EventPostArgsSchema, EventClosePostArgsSchema)


blp = Blueprint(
    'Events',
    __name__,
    url_prefix='/events',
    description="Operations on events"
)


@blp.route('/states')
class EventStatesViews(MethodView):

    @blp.response(200, EventStateSchema(many=True))
    def get(self):
        """List event states"""
        return db.session.query(EventState).all()


@blp.route('/levels')
class EventLevelsViews(MethodView):

    @blp.response(200, EventLevelSchema(many=True))
    def get(self):
        """List event levels"""
        return db.session.query(EventLevel).all()


@blp.route('/targets')
class EventTargetsViews(MethodView):

    @blp.response(200, EventTargetSchema(many=True))
    def get(self):
        """List event targets"""
        return db.session.query(EventTarget).all()


@blp.route('/categories')
class EventCategoriesViews(MethodView):

    @blp.response(200, EventCategorySchema(many=True))
    def get(self):
        """List event categories"""
        return db.session.query(EventCategory).all()


@blp.route('/')
class EventsViews(MethodView):

    @blp.etag
    @blp.arguments(EventQueryArgsSchema, location='query')
    @blp.response(200, EventSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List events"""
        return db.session.query(Event).filter_by(**args)

    @blp.etag
    @blp.arguments(EventPostArgsSchema)
    @blp.response(201, EventSchema)
    def post(self, new_item):
        """Add a new event

        Create an event with a `NEW` state.
        """
        item = Event.open(**new_item)
        db.session.commit()
        return item


@blp.route('/<int:item_id>')
class EventsByIdViews(MethodView):

    @blp.etag
    @blp.response(200, EventSchema)
    def get(self, item_id):
        """Get en event by its ID"""
        item = Event.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

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


@blp.route('/<int:item_id>/extend', methods=('PUT',))
@blp.etag
@blp.response(201, EventSchema)
@blp.alt_response(400, ErrorSchema)
def put_extend(item_id):
    """Extend an event

    Mainly change the state of the event to `ONGOING` and update
    `timestamp_last_update`.
    Returns a *400* status code if the event is `CLOSED`.
    """
    item = Event.get_by_id(item_id)
    if item is None:
        abort(404)
    blp.check_etag(item, EventSchema)
    try:
        item.extend()
    except EventError as exc:
        abort(400, str(exc))
    db.session.commit()
    return item


@blp.route('/<int:item_id>/close', methods=('PUT',))
@blp.etag
@blp.arguments(EventClosePostArgsSchema)
@blp.response(201, EventSchema)
def put_close(args, item_id):
    """Close an event

    Mainly change the state of the event to `CLOSED` and update
    `timestamp_last_update`. Nothing is done if the event is already `CLOSED`.
    """
    item = Event.get_by_id(item_id)
    if item is None:
        abort(404)
    blp.check_etag(item, EventSchema)
    item.close(**args)
    db.session.commit()
    return item
