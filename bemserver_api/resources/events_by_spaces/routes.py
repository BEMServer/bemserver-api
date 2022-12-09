"""Events by spaces resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventBySpace
from bemserver_core.exceptions import BEMServerCoreCampaignError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EventBySpaceSchema,
    EventBySpaceQueryArgsSchema,
)


blp = Blueprint(
    "EventBySpace",
    __name__,
    url_prefix="/events_by_spaces",
    description="Operations on event x space associations",
)


@blp.route("/")
class EventBySpaceViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventBySpaceQueryArgsSchema, location="query")
    @blp.response(200, EventBySpaceSchema(many=True))
    def get(self, args):
        """List event x space associations"""
        return EventBySpace.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventBySpaceSchema)
    @blp.response(201, EventBySpaceSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event x space association"""
        item = EventBySpace.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class EventBySpaceByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventBySpaceSchema)
    def get(self, item_id):
        """Get event x space association ID"""
        item = EventBySpace.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event x space association"""
        item = EventBySpace.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
