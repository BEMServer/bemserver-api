"""Event states resources"""

from flask.views import MethodView

from bemserver_core.model import EventState

from bemserver_api import Blueprint

from .schemas import EventStateSchema


blp = Blueprint(
    "Events states",
    __name__,
    url_prefix="/event_states",
    description="Operations on event states",
)


@blp.route("/")
class EventStatesViews(MethodView):
    @blp.login_required
    @blp.response(200, EventStateSchema(many=True))
    def get(self):
        """List event states"""
        return EventState.get()
