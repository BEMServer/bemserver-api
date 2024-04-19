"""Authentication"""

import base64
import datetime as dt
from functools import wraps

import sqlalchemy as sqla

import flask

from flask_smorest import abort

from joserfc import jwt
from joserfc.errors import JoseError
from joserfc.jwk import OctKey

from bemserver_core.authorization import BEMServerAuthorizationError, CurrentUser
from bemserver_core.model.users import User

from bemserver_api.database import db
from bemserver_api.exceptions import BEMServerAPIAuthenticationError


class Auth:
    """Authentication and authorization management"""

    HEADER = {"alg": "HS256"}
    TOKEN_LIFETIME = 900

    GET_USER_FUNCS = {
        "Bearer": "get_user_jwt",
        "Basic": "get_user_http_basic_auth",
    }

    def __init__(self, app=None):
        self.key = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.key = OctKey.import_key(app.config["SECRET_KEY"])
        self.get_user_funcs = {
            k: getattr(self, v)
            for k, v in self.GET_USER_FUNCS.items()
            if k in app.config["AUTH_METHODS"]
        }

    def encode(self, user):
        claims = {
            "email": user.email,
            "exp": dt.datetime.now(tz=dt.timezone.utc)
            + dt.timedelta(seconds=self.TOKEN_LIFETIME),
        }
        return jwt.encode(self.HEADER, claims, self.key)

    def decode(self, text):
        return jwt.decode(text, self.key)

    def validate_token(self, token):
        claims_requests = jwt.JWTClaimsRegistry(email={"essential": True})
        claims_requests.validate(token.claims)

    def get_user_jwt(self, creds):
        try:
            token = self.decode(creds)
        except (ValueError, JoseError) as exc:
            raise (BEMServerAPIAuthenticationError) from exc
        try:
            self.validate_token(token)
        except JoseError as exc:
            raise (BEMServerAPIAuthenticationError) from exc

        user_email = token.claims["email"]
        user = db.session.execute(
            sqla.select(User).where(User.email == user_email)
        ).scalar()
        if user is None:
            raise (BEMServerAPIAuthenticationError)
        return user

    @staticmethod
    def get_user_http_basic_auth(creds):
        """Check password and return User instance"""
        try:
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

    def get_user(self):
        if (auth_header := flask.request.headers.get("Authorization")) is None:
            raise BEMServerAPIAuthenticationError
        try:
            scheme, creds = auth_header.split(" ", maxsplit=1)
        except ValueError as exc:
            raise BEMServerAPIAuthenticationError from exc
        try:
            func = self.get_user_funcs[scheme]
        except KeyError as exc:
            raise BEMServerAPIAuthenticationError from exc
        return func(creds.encode("utf-8"))

    def login_required(self, f=None, **kwargs):
        """Decorator providing authentication and authorization

        Uses JWT or HTTPBasicAuth.login_required to authenticate user
        Sets CurrentUser context variable to authenticated user for the request
        Catches Authorization error and aborts accordingly
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **func_kwargs):
                try:
                    user = self.get_user()
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
