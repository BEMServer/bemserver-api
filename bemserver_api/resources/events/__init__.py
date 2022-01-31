from .routes import blp
from .timeseries.routes import blp as timeseries_blp


def register_blueprints(api):
    api.register_blueprint(blp)
    api.register_blueprint(timeseries_blp)
