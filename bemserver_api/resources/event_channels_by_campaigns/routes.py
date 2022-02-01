"""Event channels by campaigns resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventChannelByCampaign

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import EventChannelByCampaignSchema, EventChannelByCampaignQueryArgsSchema


blp = Blueprint(
    "Event channels by campaigns",
    __name__,
    url_prefix="/event_channels_by_campaigns",
    description="Operations on event channel x campaign associations",
)


@blp.route("/")
class EventChannelByCampaignViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelByCampaignQueryArgsSchema, location="query")
    @blp.response(200, EventChannelByCampaignSchema(many=True))
    def get(self, args):
        """List event channel x campaign associations"""
        return EventChannelByCampaign.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelByCampaignSchema)
    @blp.response(201, EventChannelByCampaignSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event channel x campaign association"""
        item = EventChannelByCampaign.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EventChannelByCampaignByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventChannelByCampaignSchema)
    def get(self, item_id):
        """Get event channel x campaign association by ID"""
        item = EventChannelByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a event channel x campaign association"""
        item = EventChannelByCampaign.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
