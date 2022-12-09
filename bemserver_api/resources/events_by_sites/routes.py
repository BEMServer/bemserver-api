"""Events by sites resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventBySite
from bemserver_core.exceptions import BEMServerCoreCampaignError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EventBySiteSchema,
    EventBySiteQueryArgsSchema,
)


blp = Blueprint(
    "EventBySite",
    __name__,
    url_prefix="/events_by_sites",
    description="Operations on event x site associations",
)


@blp.route("/")
class EventBySiteViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventBySiteQueryArgsSchema, location="query")
    @blp.response(200, EventBySiteSchema(many=True))
    def get(self, args):
        """List event x site associations"""
        return EventBySite.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventBySiteSchema)
    @blp.response(201, EventBySiteSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event x site association"""
        item = EventBySite.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class EventBySiteByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventBySiteSchema)
    def get(self, item_id):
        """Get event x site association ID"""
        item = EventBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event x site association"""
        item = EventBySite.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
