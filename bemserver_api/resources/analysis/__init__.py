from .routes import blp4c  # noqa


def register_blueprints(api):
    api.register_blueprint(blp4c)
