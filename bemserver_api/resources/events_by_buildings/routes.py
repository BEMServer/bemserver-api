"""Events by buildings resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventByBuilding
from bemserver_core.exceptions import BEMServerCoreCampaignError

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EventByBuildingSchema,
    EventByBuildingQueryArgsSchema,
)


blp = Blueprint(
    "EventByBuilding",
    __name__,
    url_prefix="/events_by_buildings",
    description="Operations on event x building associations",
)


@blp.route("/")
class EventByBuildingViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventByBuildingQueryArgsSchema, location="query")
    @blp.response(200, EventByBuildingSchema(many=True))
    def get(self, args):
        """List event x building associations"""
        return EventByBuilding.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventByBuildingSchema)
    @blp.response(201, EventByBuildingSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event x building association"""
        item = EventByBuilding.new(**new_item)
        try:
            db.session.commit()
        except BEMServerCoreCampaignError as exc:
            abort(422, errors={"json": {"_schema": str(exc)}})
        return item


@blp.route("/<int:item_id>")
class EventByBuildingByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventByBuildingSchema)
    def get(self, item_id):
        """Get event x building association ID"""
        item = EventByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event x building association"""
        item = EventByBuilding.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
