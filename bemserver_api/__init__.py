"""BEMServer API"""

import flask
from werkzeug.middleware.profiler import ProfilerMiddleware

from bemserver_core import BEMServerCore

from . import database
from .extensions import (  # noqa
    Api,
    Blueprint,
    Schema,
    AutoSchema,
    SQLCursorPage,
    authentication,
)
from .resources import register_blueprints


__version__ = "0.22.0"

API_VERSION = __version__
OPENAPI_VERSION = "3.1.0"


def create_app():
    """Create application"""
    app = flask.Flask(__name__)
    app.config.from_object("bemserver_api.settings.Config")
    app.config.from_envvar("BEMSERVER_API_SETTINGS_FILE", silent=True)

    database.init_app(app)
    api = Api(
        spec_kwargs={
            "version": API_VERSION,
            "openapi_version": OPENAPI_VERSION,
        }
    )
    api.init_app(app)
    register_blueprints(api)

    BEMServerCore()

    if profile_dir := app.config["PROFILE_DIR"]:
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app, stream=None, profile_dir=profile_dir
        )

    return app
