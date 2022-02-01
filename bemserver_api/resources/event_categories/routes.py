"""Event categories resources"""

from flask.views import MethodView

from bemserver_core.model import EventCategory

from bemserver_api import Blueprint

from .schemas import EventCategorySchema


blp = Blueprint(
    "Event categories",
    __name__,
    url_prefix="/event_categories",
    description="Operations on event categories",
)


@blp.route("/")
class EventCategoriesViews(MethodView):
    @blp.login_required
    @blp.response(200, EventCategorySchema(many=True))
    def get(self):
        """List event categories"""
        return EventCategory.get()
