"""Notifications resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Notification

from bemserver_api import Blueprint, SQLCursorPage
from bemserver_api.database import db

from .schemas import (
    NotificationSchema,
    NotificationPutSchema,
    NotificationQueryArgsSchema,
    NotificationCountByCampaignSchema,
    NotificationCountByCampaignQueryArgsSchema,
    NotificationMarkAllAsReadQueryArgsSchema,
)


blp = Blueprint(
    "Notification",
    __name__,
    url_prefix="/notifications",
    description="Operations on notifications",
)


@blp.route("/")
class NotificationsViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(NotificationQueryArgsSchema, location="query")
    @blp.response(200, NotificationSchema(many=True))
    @blp.paginate(SQLCursorPage)
    def get(self, args):
        """List notifications"""
        return Notification.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(NotificationSchema)
    @blp.response(201, NotificationSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new notification"""
        item = Notification.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<string:item_id>")
class NotificationsByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, NotificationSchema)
    def get(self, item_id):
        """Get a notification by its by ID"""
        item = Notification.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.arguments(NotificationPutSchema)
    @blp.response(200, NotificationSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing notification"""
        item = Notification.get_by_id(item_id)
        if item is None:
            abort(404)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.response(204)
    def delete(self, item_id):
        """Delete a notification"""
        item = Notification.get_by_id(item_id)
        if item is None:
            abort(404)
        item.delete()
        db.session.commit()


@blp.get("/count_by_campaign")
@blp.login_required
@blp.etag
@blp.arguments(NotificationCountByCampaignQueryArgsSchema, location="query")
@blp.response(200, NotificationCountByCampaignSchema)
def count_by_campaign(args):
    """Get notification count by campaign"""
    return Notification.get_count_by_campaign(**args)


@blp.put("/mark_all_as_read")
@blp.login_required
@blp.arguments(NotificationMarkAllAsReadQueryArgsSchema, location="query")
@blp.response(204)
def mark_all_as_read(args):
    """Mark all notifications as read"""
    Notification.mark_all_as_read(**args)
    db.session.commit()
