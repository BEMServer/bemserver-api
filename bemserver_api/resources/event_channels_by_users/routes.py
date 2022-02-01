"""Event channels by users resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventChannelByUser

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import EventChannelByUserSchema, EventChannelByUserQueryArgsSchema


blp = Blueprint(
    "Event channels by users",
    __name__,
    url_prefix="/event_channels_by_users",
    description="Operations on event channel x user associations",
)


@blp.route("/")
class EventChannelByUserViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelByUserQueryArgsSchema, location="query")
    @blp.response(200, EventChannelByUserSchema(many=True))
    def get(self, args):
        """List event channel x user associations"""
        return EventChannelByUser.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelByUserSchema)
    @blp.response(201, EventChannelByUserSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event channel x user association"""
        item = EventChannelByUser.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EventChannelByUserByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventChannelByUserSchema)
    def get(self, item_id):
        """Get event channel x user association by ID"""
        item = EventChannelByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.response(204)
    @blp.catch_integrity_error
    def delete(self, item_id):
        """Delete a event channel x user association"""
        item = EventChannelByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()
