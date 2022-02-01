"""Event levels resources"""

from flask.views import MethodView

from bemserver_core.model import EventLevel

from bemserver_api import Blueprint

from .schemas import EventLevelSchema


blp = Blueprint(
    "Event levels",
    __name__,
    url_prefix="/event_levels",
    description="Operations on event levels",
)


@blp.route("/")
class EventLevelsViews(MethodView):
    @blp.login_required
    @blp.response(200, EventLevelSchema(many=True))
    def get(self):
        """List event levels"""
        return EventLevel.get()
