"""BEMServer API"""
import flask

from bemserver_core import BEMServerCore

from . import database
from .extensions import (  # noqa
    Api,
    Blueprint,
    Schema,
    AutoSchema,
    SQLCursorPage,
    SortField,
    authentication,
)
from .resources import register_blueprints


__version__ = "0.2.0"


def create_app(config_override=None):
    """Create application

    :param type config_override: Config class overriding default config.
        Used for tests.
    """
    app = flask.Flask(__name__)
    app.config.from_object("bemserver_api.settings.Config")
    app.config.from_envvar("FLASK_SETTINGS_FILE", silent=True)
    app.config.from_object(config_override)

    database.init_app(app)
    api = Api()
    api.init_app(app)
    register_blueprints(api)

    bsc = BEMServerCore()
    bsc.init_auth()

    return app
