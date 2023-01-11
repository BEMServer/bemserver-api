"""Notifications resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import Notification

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    NotificationSchema,
    NotificationPutSchema,
    NotificationsQueryArgsSchema,
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
    @blp.arguments(NotificationsQueryArgsSchema, location="query")
    @blp.response(200, NotificationSchema(many=True))
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
    @blp.etag
    @blp.arguments(NotificationPutSchema)
    @blp.response(200, NotificationSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing notification"""
        item = Notification.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, NotificationSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete a notification"""
        item = Notification.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, NotificationSchema)
        item.delete()
        db.session.commit()
