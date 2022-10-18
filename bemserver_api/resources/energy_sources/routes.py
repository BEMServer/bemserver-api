"""Energy sources resources"""

from flask.views import MethodView

from bemserver_core.model import EnergySource

from bemserver_api import Blueprint

from .schemas import EnergySourceSchema


blp = Blueprint(
    "EnergySource",
    __name__,
    url_prefix="/energy_sources",
    description="Operations on energy sources",
)


@blp.route("/")
class EnergySourceViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EnergySourceSchema(many=True))
    def get(self):
        """List energy sources"""
        return EnergySource.get()
