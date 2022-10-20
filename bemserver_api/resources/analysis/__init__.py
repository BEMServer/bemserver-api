"""Analysis resources"""
from bemserver_api import Blueprint

from .completeness.routes import blp as completeness_blp
from .energy_consumption.routes import blp as energy_consumption_blp


blp = Blueprint(
    "Analysis", __name__, url_prefix="/analysis", description="Data analysis operations"
)


blp.register_blueprint(completeness_blp)
blp.register_blueprint(energy_consumption_blp)


def register_blueprints(api):
    api.register_blueprint(blp)
