"""Database access"""
from bemserver_core.database import db


def init_app(app):
    """Init DB accessor with app

    Adds app contextteardown method to close DB session.
    """

    @app.teardown_appcontext
    def cleanup(_):
        db.session.remove()
