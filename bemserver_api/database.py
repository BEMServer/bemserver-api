"""Database access"""
from bemserver_core.database import db


def init_app(app):
    """Init DB accessor with app

    Sets DB engine using app config.
    Adds app contextteardown method to close DB session.
    """
    db.set_db_url(app.config["SQLALCHEMY_DATABASE_URI"])

    @app.teardown_appcontext
    def cleanup(_):
        db.session.remove()
