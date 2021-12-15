from .routes import blp
from .timeseries import routes  # noqa


def register_blueprints(api):
    api.register_blueprint(blp)
