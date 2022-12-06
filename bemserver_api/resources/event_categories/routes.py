"""Event categories resources"""

from flask.views import MethodView
from flask_smorest import abort

from bemserver_core.model import EventCategory

from bemserver_api import Blueprint
from bemserver_api.database import db

from .schemas import EventCategorySchema


blp = Blueprint(
    "EventCategory",
    __name__,
    url_prefix="/event_categories",
    description="Operations on event categories",
)


@blp.route("/")
class EventCategoriesViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventCategorySchema(many=True))
    def get(self):
        """List event categories"""
        return EventCategory.get()

    @blp.login_required
    @blp.etag
    @blp.arguments(EventCategorySchema)
    @blp.response(201, EventCategorySchema)
    @blp.catch_integrity_error
    def post(self, new_item):
        """Add a new event"""
        item = EventCategory.new(**new_item)
        db.session.commit()
        return item


@blp.route("/<string:item_id>")
class EventCategoriesByIdViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EventCategorySchema)
    def get(self, item_id):
        """Get en event by its ID"""
        item = EventCategory.get_by_id(item_id)
        if item is None:
            abort(404)
        return item

    @blp.login_required
    @blp.etag
    @blp.arguments(EventCategorySchema)
    @blp.response(200, EventCategorySchema)
    @blp.catch_integrity_error
    def put(self, new_item, item_id):
        """Update an existing timeseries"""
        item = EventCategory.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EventCategorySchema)
        item.update(**new_item)
        db.session.commit()
        return item

    @blp.login_required
    @blp.etag
    @blp.response(204)
    def delete(self, item_id):
        """Delete an event"""
        item = EventCategory.get_by_id(item_id)
        if item is None:
            abort(404)
        blp.check_etag(item, EventCategorySchema)
        item.delete()
        db.session.commit()
