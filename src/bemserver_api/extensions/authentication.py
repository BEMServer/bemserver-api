"""Authentication"""

import base64
import datetime as dt
from datetime import datetime
from functools import wraps

import sqlalchemy as sqla

import flask

from flask_smorest import abort

import requests
from authlib.jose import JsonWebToken
from authlib.jose.errors import ExpiredTokenError, JoseError

from bemserver_core.authorization import BEMServerAuthorizationError, CurrentUser
from bemserver_core.model.users import User

from bemserver_api.database import db
from bemserver_api.exceptions import BEMServerAPIAuthenticationError

# https://docs.authlib.org/en/latest/jose/jwt.html#jwt-with-limited-algorithms
jwt = JsonWebToken(["HS256"])


class OAuth:
    """OAuth authentication management"""

    def __init__(self, app=None):
        self.auth_url = None
        self.token_url = None
        self.client_id = None
        self.client_secret = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        # TODO: .well-known/openid-configuration
        # f"https://github.com/login/oauth/authorize?client_id={os.environ.get('GITHUB_CLIENT_ID')}"
        self.auth_url = app.config["OAUTH_AUTH_URL"]
        # "https://github.com/login/oauth/access_token"
        self.token_url = app.config["OAUTH_TOKEN_URL"]
        self.user_info_url = app.config["OAUTH_USER_INFO_URL"]
        self.client_id = app.config["OAUTH_CLIENT_ID"]
        self.client_secret = app.config["OAUTH_CLIENT_SECRET"]

    def get_token(self, code):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
        }
        try:
            response = requests.post(self.token_url, json=params)
            response.raise_for_status()
            access_token = response.json().get("access_token")
        except Exception as e:
            print(f"Error fetching token: {e}")
        return access_token

    def get_user_info(self, token):
        # TODO: or get_user_email?
        headers = {"Authorization": f"token {token}"}
        try:
            response = requests.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            user_info = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user info: {e}")
        return user_info

    def get_user(self, token):
        user_info = self.get_user_info(token)
        # TODO: config?
        # https://openid.net/specs/openid-connect-core-1_0.html#UserInfo
        user = self.get_user_by_email(user_info["email"])
        return {
            "status": "success",
            "access_token": auth.encode(user).decode("utf-8"),
            "refresh_token": auth.encode(user, token_type="refresh").decode("utf-8"),
        }

    @staticmethod
    def get_user_by_email(user_email):
        return db.session.execute(
            sqla.select(User).where(User.email == user_email)
        ).scalar()


class Auth:
    """Authentication and authorization management"""

    HEADER = {"alg": "HS256"}
    ACCESS_TOKEN_LIFETIME = 60 * 15  # 15 minutes
    REFRESH_TOKEN_LIFETIME = 60 * 60 * 24 * 60  # 2 months

    GET_USER_FUNCS = {
        "Bearer": "get_user_jwt",
        "Basic": "get_user_http_basic_auth",
    }

    def __init__(self, app=None):
        self.key = None
        self.get_user_funcs = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.key = app.config["SECRET_KEY"]
        self.auth_methods = app.config["AUTH_METHODS"]
        self.get_user_funcs = {
            k: getattr(self, v)
            for k, v in self.GET_USER_FUNCS.items()
            if k in self.auth_methods
        }

    def encode(self, user, token_type="access"):
        token_lifetime = (
            self.ACCESS_TOKEN_LIFETIME
            if token_type == "access"
            else self.REFRESH_TOKEN_LIFETIME
        )
        claims = {
            "email": user.email,
            # datetime is imported in module namespace to allow test mock
            # kinda sucks, but oh well...
            "exp": datetime.now(tz=dt.timezone.utc)
            + dt.timedelta(seconds=token_lifetime),
            "type": token_type,
        }
        return jwt.encode(self.HEADER.copy(), claims, self.key)

    def decode(self, text):
        return jwt.decode(
            text,
            self.key,
            claims_options={
                "email": {"essential": True},
                "type": {"essential": True},
            },
        )

    @staticmethod
    def get_user_by_email(user_email):
        return db.session.execute(
            sqla.select(User).where(User.email == user_email)
        ).scalar()

    def get_user_jwt(self, creds, refresh=False):
        try:
            claims = self.decode(creds)
            claims.validate()
        except ExpiredTokenError as exc:
            raise BEMServerAPIAuthenticationError(code="expired_token") from exc
        except JoseError as exc:
            raise BEMServerAPIAuthenticationError(code="invalid_token") from exc
        if refresh is not (claims["type"] == "refresh"):
            raise BEMServerAPIAuthenticationError(code="invalid_token")
        user_email = claims["email"]
        if (user := self.get_user_by_email(user_email)) is None:
            raise BEMServerAPIAuthenticationError(code="invalid_token")
        return user

    def get_user_http_basic_auth(self, creds, **_kwargs):
        """Check password and return User instance"""
        try:
            enc_email, enc_password = base64.b64decode(creds).split(b":", maxsplit=1)
            user_email = enc_email.decode()
            password = enc_password.decode()
        except (ValueError, TypeError) as exc:
            raise BEMServerAPIAuthenticationError(code="malformed_credentials") from exc
        if (user := self.get_user_by_email(user_email)) is None:
            raise BEMServerAPIAuthenticationError(code="invalid_credentials")
        if not user.check_password(password):
            raise BEMServerAPIAuthenticationError(code="invalid_credentials")
        return user

    def get_user(self, refresh=False):
        if (auth_header := flask.request.headers.get("Authorization")) is None:
            raise BEMServerAPIAuthenticationError(code="missing_authentication")
        try:
            scheme, creds = auth_header.split(" ", maxsplit=1)
        except ValueError:
            abort(400)
        try:
            func = self.get_user_funcs[scheme]
        except KeyError as exc:
            raise BEMServerAPIAuthenticationError(code="invalid_scheme") from exc
        return func(creds.encode("utf-8"), refresh=refresh)

    def login_required(self, f=None, refresh=False):
        """Decorator providing authentication and authorization

        Uses JWT or HTTPBasicAuth.login_required to authenticate user
        Sets CurrentUser context variable to authenticated user for the request
        Catches Authorization error and aborts accordingly
        """

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **func_kwargs):
                try:
                    user = self.get_user(refresh=refresh)
                except BEMServerAPIAuthenticationError as exc:
                    abort(
                        401,
                        "Authentication error",
                        errors={"authentication": exc.code},
                        headers={"WWW-Authenticate": ", ".join(self.auth_methods)},
                    )
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
