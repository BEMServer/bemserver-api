from .routes import blp


def register_blueprints(api):
    api.register_blueprint(blp)
