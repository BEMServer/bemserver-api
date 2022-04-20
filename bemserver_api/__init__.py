"""BEMServer API"""
import importlib

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
    authentication.init_app(app)
    api = Api()
    api.init_app(app)
    register_blueprints(api)

    bsc = BEMServerCore()
    for path in app.config["PLUGINS"]:
        mod, cls = path.rsplit(".", 1)
        plugin = getattr(importlib.import_module(mod), cls)()
        # Load plugin in BEMServer core
        bsc.load_plugin(plugin)
        # Register plugin API blueprint (if any)
        blp = plugin.API_BLUEPRINT
        if blp is not None:
            api.register_blueprint(blp, url_prefix=f"/plugins{blp.url_prefix}")
    bsc.init_auth()

    return app
