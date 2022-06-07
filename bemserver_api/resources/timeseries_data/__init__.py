from .routes import blp, blp4c


def register_blueprints(api):
    api.register_blueprint(blp)
    api.register_blueprint(blp4c)
