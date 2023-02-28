"""Energies resources"""

from flask.views import MethodView

from bemserver_core.model import Energy

from bemserver_api import Blueprint

from .schemas import EnergySchema


blp = Blueprint(
    "Energy",
    __name__,
    url_prefix="/energies",
    description="Operations on energies",
)


@blp.route("/")
class EnergyViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EnergySchema(many=True))
    def get(self):
        """List energies"""
        return Energy.get()
