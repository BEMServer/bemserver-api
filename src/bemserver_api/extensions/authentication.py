"""Authentication"""

import base64
from functools import wraps

import sqlalchemy as sqla

import flask

from flask_smorest import abort

from bemserver_core.authorization import BEMServerAuthorizationError, CurrentUser
from bemserver_core.model.users import User

from bemserver_api.database import db
from bemserver_api.exceptions import BEMServerAPIAuthenticationError


class Auth:
    """Authentication and authorization management"""

    @staticmethod
    def get_user_http_basic_auth():
        """Check password and return User instance"""
        if (auth_header := flask.request.headers.get("Authorization")) is None:
            raise (BEMServerAPIAuthenticationError)
        try:
            _, creds = auth_header.encode("utf-8").split(b" ", maxsplit=1)
            enc_email, enc_password = base64.b64decode(creds).split(b":", maxsplit=1)
            user_email = enc_email.decode()
            password = enc_password.decode()
        except (ValueError, TypeError) as exc:
            raise (BEMServerAPIAuthenticationError) from exc
        user = db.session.execute(
            sqla.select(User).where(User.email == user_email)
        ).scalar()
        if user is None or not user.check_password(password):
            raise (BEMServerAPIAuthenticationError)
        return user

    def login_required(self, f=None, **kwargs):
        """Decorator providing authentication and authorization

        Uses HTTPBasicAuth.login_required authenticate user
        Sets CurrentUser context variable to authenticated user for the request
        Catches Authorization error and aborts accordingly
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **func_kwargs):
                try:
                    user = self.get_user_http_basic_auth()
                except BEMServerAPIAuthenticationError:
                    abort(401, "Authentication error")
                with CurrentUser(user):
                    try:
                        resp = func(*args, **func_kwargs)
                    except BEMServerAuthorizationError:
                        abort(403, message="Authorization error")
                return resp

            return wrapper

        if f:
            return decorator(f)
        return decorator


auth = Auth()
