"""Even categories by users resources"""
from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventCategoryByUser

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import (
    EventCategoryByUserSchema,
    EventCategoryByUserPutSchema,
    EventCategoryByUserQueryArgsSchema,
)


blp = Blueprint(
    "EventCategoryByUser",
    __name__,
    url_prefix="/event_categories_by_users",
    description="Operations on event category x user associations",
)


@blp.route("/")
class EventCategoryByUserViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.arguments(EventCategoryByUserQueryArgsSchema, location="query")
    @blp.response(200, EventCategoryByUserSchema(many=True))
    def get(self, args):
        """List event category x user associations"""
        return EventCategoryByUser.get(**args)

    @blp.login_required
    @blp.etag
    @blp.arguments(EventCategoryByUserSchema)
    @blp.response(201, EventCategoryByUserSchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event category x user association"""
        item = EventCategoryByUser.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<int:item_id>")
class EventCategoryByUserByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventCategoryByUserSchema)
    def get(self, item_id):
        """Get event category x user association by ID"""
        item = EventCategoryByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(EventCategoryByUserPutSchema)
    @blp.response(200, EventCategoryByUserSchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing  event category x user association"""
        item = EventCategoryByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EventCategoryByUserSchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event category x user association"""
        item = EventCategoryByUser.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EventCategoryByUserSchema)
        item.delete()
        db.session.commit()
