"""BEMServer API"""
import flask
import click

from . import database
from .extensions import (  # noqa
    Api, Blueprint, Schema, AutoSchema, SQLCursorPage, authentication
)
from .resources import register_blueprints


@click.command()
@flask.cli.with_appcontext
def setup_db():
    database.db.setup_tables()


def create_app(config_override=None):
    """Create application

    :param type config_override: Config class overriding default config.
        Used for tests.
    """
    app = flask.Flask(__name__)
    app.config.from_object("bemserver_api.settings.Config")
    app.config.from_envvar('FLASK_SETTINGS_FILE', silent=True)
    app.config.from_object(config_override)

    database.init_app(app)
    authentication.init_app(app)
    api = Api()
    api.init_app(app)
    register_blueprints(api)

    app.cli.add_command(setup_db)

    return app
