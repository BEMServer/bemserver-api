"""Event channels resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventChannel

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import EventChannelSchema, EventChannelQueryArgsSchema


blp = Blueprint(
    "Event channels",
    __name__,
    url_prefix="/event_channels",
    description="Operations on event channels",
)


@blp.route("/")
class EventChannelViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelQueryArgsSchema, location="query")
    @blp.response(200, EventChannelSchema(many=True))
    def get(self, args):
        """List event channels"""
        return EventChannel.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelSchema)
    @blp.response(201, EventChannelSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event channel"""
        item = EventChannel.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EventChannelByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventChannelSchema)
    def get(self, item_id):
        """Get event channel by ID"""
        item = EventChannel.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelSchema)
    @blp.response(200, EventChannelSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing event channel"""
        item = EventChannel.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EventChannelSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a event channel"""
        item = EventChannel.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EventChannelSchema)
        item.delete()
        db.session.commit()
