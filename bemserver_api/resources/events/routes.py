"""Events resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import (
    EventState, EventCategory, EventLevel,
    EventChannel, EventChannelByCampaign,)

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EventStateSchema, EventCategorySchema, EventLevelSchema,
    EventChannelSchema, EventChannelQueryArgsSchema,
    EventChannelByCampaignSchema, EventChannelByCampaignQueryArgsSchema,
)


blp = Blueprint(
    'Events',
    __name__,
    url_prefix='/events',
    description="Operations on events"
)


@blp.route('/states')
class EventStatesViews(MethodView):

    @blp.login_required
    @blp.response(200, EventStateSchema(many=True))
    def get(self):
        """List event states"""
        return EventState.get()


@blp.route('/levels')
class EventLevelsViews(MethodView):

    @blp.login_required
    @blp.response(200, EventLevelSchema(many=True))
    def get(self):
        """List event levels"""
        return EventLevel.get()


@blp.route('/categories')
class EventCategoriesViews(MethodView):

    @blp.login_required
    @blp.response(200, EventCategorySchema(many=True))
    def get(self):
        """List event categories"""
        return EventCategory.get()


@blp.route('/channels/')
class EventChannelViews(MethodView):

    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelQueryArgsSchema, location='query')
    @blp.response(200, EventChannelSchema(many=True))
    def get(self, args):
        """List campaigns"""
        return EventChannel.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelSchema)
    @blp.response(201, EventChannelSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new campaign"""
        item = EventChannel.new(**new_item)
        db.session.commit()
        return item


@blp.route('/channels/<int:item_id>')
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


@blp.route('/channelsbycampaigns/')
class EventChannelByCampaignViews(MethodView):

    @blp.login_required
    @blp.etag
    @blp.arguments(EventChannelByCampaignQueryArgsSchema, location='query')
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


@blp.route('/channelsbycampaigns/<int:item_id>')
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
