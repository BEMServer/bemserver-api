"""Energy end uses resources"""

from flask.views import MethodView

from bemserver_core.model import EnergyEndUse

from bemserver_api import Blueprint

from .schemas import EnergyEndUseSchema


blp = Blueprint(
    "EnergyEndUse",
    __name__,
    url_prefix="/energy_end_uses",
    description="Operations on energy end uses",
)


@blp.route("/")
class EnergyEndUseViews(MethodView):
    @blp.login_required
    @blp.etag
    @blp.response(200, EnergyEndUseSchema(many=True))
    def get(self):
        """List energy end uses"""
        return EnergyEndUse.get()
