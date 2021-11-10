"""Authentication"""
from functools import wraps

import sqlalchemy as sqla
from flask_httpauth import HTTPBasicAuth
from flask_smorest import abort
from bemserver_core.model.users import User
from bemserver_core.auth import CurrentUser, BEMServerAuthorizationError

from bemserver_api.database import db


class Auth(HTTPBasicAuth):
    """Authentication and authorization management"""

    def login_required(self, f=None, role=None, optional=None):
        """Decorator providing authentication and authorization

        Uses HTTPBasicAuth.login_required authenticate user
        Sets CurrentUser context variable to authenticated user for the request
        Catches Authorization error and aborts accordingly
        """
        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                with CurrentUser(self.current_user()):
                    try:
                        resp = func(*args, **kwargs)
                    except BEMServerAuthorizationError:
                        abort(403, message="Authorization error")
                return resp

            # Wrap this inside HTTPAuth.login_required
            # to get authenticated user
            return super(Auth, self).login_required(
                role=role, optional=optional
            )(wrapper)

        if f:
            return decorator(f)
        return decorator


auth = Auth()


def init_app(app):
    """Initialize application authentication"""

    @auth.verify_password
    def verify_password(username, password):
        user = db.session.execute(
            sqla.select(User).where(User.email == username)
        ).scalar()
        if user is not None:
            user.check_password(password)
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
