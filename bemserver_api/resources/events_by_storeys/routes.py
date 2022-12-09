"""Events by storeys resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventByStorey
from bemserver_core.exceptions import BEMServerCoreCampaignError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EventByStoreySchema,
    EventByStoreyQueryArgsSchema,
)


blp = Blueprint(
    "EventByStorey",
    __name__,
    url_prefix="/events_by_storeys",
    description="Operations on event x storey associations",
)


@blp.route("/")
class EventByStoreyViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventByStoreyQueryArgsSchema, location="query")
    @blp.response(200, EventByStoreySchema(many=True))
    def get(self, args):
        """List event x storey associations"""
        return EventByStorey.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventByStoreySchema)
    @blp.response(201, EventByStoreySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event x storey association"""
        item = EventByStorey.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class EventByStoreyByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventByStoreySchema)
    def get(self, item_id):
        """Get event x storey association ID"""
        item = EventByStorey.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event x storey association"""
        item = EventByStorey.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
