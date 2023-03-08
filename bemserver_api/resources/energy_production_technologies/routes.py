"""Energy end uses resources"""

from flask.views import MethodView

from bemserver_core.model import EnergyProductionTechnology

from bemserver_api import Blueprint

from .schemas import EnergyProductionTechnologySchema


blp = Blueprint(
    "EnergyProductionTechnology",
    __name__,
    url_prefix="/energy_production_technologies",
    description="Operations on energy production technologies",
)


@blp.route("/")
class EnergyProductionTechnologyViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EnergyProductionTechnologySchema(many=True))
    def get(self):
        """List energy production technologies"""
        return EnergyProductionTechnology.get()
