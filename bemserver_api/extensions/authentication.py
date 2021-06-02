"""Authentication"""
import sqlalchemy as sqla
from flask_httpauth import HTTPBasicAuth
from flask_smorest import abort
from bemserver_core.model.users import User

from bemserver_api.database import db

auth = HTTPBasicAuth()


def init_app(app):
    """Initialize application authentication"""

    @auth.verify_password
    def verify_password(username, password):
        if not app.config.get("AUTH_ENABLED", False):
            return True

        user = db.session.execute(
            sqla.select(User).where(User.email == username)
        ).scalar()
        if (
            user is not None and
            user.is_active and
            user.check_password(password)
        ):
            return user

    @auth.error_handler
    def auth_error(status):
        # Call abort to trigger error handler and get consistent JSON output
        abort(status, message="Authentication error")

    @auth.get_user_roles
    def get_user_roles(user):
        # Authentication disabled
        if user is None or user.is_admin:
            return ("admin", )
        return ("user", )
