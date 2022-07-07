from .routes import blp  # noqa


def register_blueprints(api):
    api.register_blueprint(blp)
