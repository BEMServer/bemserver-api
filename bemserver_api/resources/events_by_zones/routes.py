"""Events by zones resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventByZone
from bemserver_core.exceptions import BEMServerCoreCampaignError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EventByZoneSchema,
    EventByZoneQueryArgsSchema,
)


blp = Blueprint(
    "EventByZone",
    __name__,
    url_prefix="/events_by_zones",
    description="Operations on event x zone associations",
)


@blp.route("/")
class EventByZoneViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventByZoneQueryArgsSchema, location="query")
    @blp.response(200, EventByZoneSchema(many=True))
    def get(self, args):
        """List event x zone associations"""
        return EventByZone.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventByZoneSchema)
    @blp.response(201, EventByZoneSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event x zone association"""
        item = EventByZone.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class EventByZoneByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventByZoneSchema)
    def get(self, item_id):
        """Get event x zone association ID"""
        item = EventByZone.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event x zone association"""
        item = EventByZone.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
