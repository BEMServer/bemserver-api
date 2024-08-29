"""Authentication resources"""

from textwrap import dedent

import flask

from bemserver_core.authorization import get_current_user

from bemserver_api import Blueprint
from bemserver_api.extensions.authentication import auth

from .schemas import GetJWTArgsSchema, GetJWTRespSchema

AUTH_BLP_DESC = dedent("""Authentication operations

The following resources are used to get and refresh tokens. When authenticating, first
get a couple of access (short-lived) and refresh (long-lived) tokens using login and
password. When or before access token expires, refresh tokens to get a new pair of
tokens with new expiration dates. If refresh token is expired, get a new pair of tokens
using login and password again.
""")


blp = Blueprint(
    "Authentication",
    __name__,
    url_prefix="/auth",
    description=AUTH_BLP_DESC,
)


@blp.route("/token", methods=["POST"])
@blp.arguments(GetJWTArgsSchema)
@blp.response(
    200,
    GetJWTRespSchema,
    examples={
        "success": {
            "value": {
                "status": "success",
                "access_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl"
                    "bWFpbCI6ImFjdGl2ZUB0ZXN0LmNvbSIsImV4cCI6M"
                    "TcxNjM2OTg4OCwidHlwZSI6ImFjY2VzcyJ9.YT-50"
                    "7Qo9oncWKKRJhRXBbpLrOCYoJOMxbk1IaAQef4"
                ),
                "refresh_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl"
                    "bWFpbCI6ImFjdGl2ZUB0ZXN0LmNvbSIsImV4cCI6M"
                    "TcyMTU1MzEzNSwidHlwZSI6InJlZnJlc2gifQ._kc"
                    "SHTzcngWIt-LRX6yBx8ftpekT_Dqo8qbPyfgFjSQ"
                ),
            },
        },
        "failure": {
            "value": {
                "status": "failure",
            },
        },
    },
)
def get_token(creds):
    """Get access and refresh tokens

    Use login and password to get a pair of access and refresh tokens.

    No authentication header needed. Credentials must be passed in request payload.
    """
    user = auth.get_user_by_email(creds["email"])
    if user is None or not user.check_password(creds["password"]) or not user.is_active:
        return flask.jsonify({"status": "failure"})
    return {
        "status": "success",
        "access_token": auth.encode(user).decode("utf-8"),
        "refresh_token": auth.encode(user, token_type="refresh").decode("utf-8"),
    }


@blp.route("/token/refresh", methods=["POST"])
@blp.login_required(refresh=True)
@blp.response(
    200,
    GetJWTRespSchema,
    examples={
        "success": {
            "value": {
                "status": "success",
                "access_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl"
                    "bWFpbCI6ImFjdGl2ZUB0ZXN0LmNvbSIsImV4cCI6M"
                    "TcxNjM2OTg4OCwidHlwZSI6ImFjY2VzcyJ9.YT-50"
                    "7Qo9oncWKKRJhRXBbpLrOCYoJOMxbk1IaAQef4"
                ),
                "refresh_token": (
                    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl"
                    "bWFpbCI6ImFjdGl2ZUB0ZXN0LmNvbSIsImV4cCI6M"
                    "TcyMTU1MzEzNSwidHlwZSI6InJlZnJlc2gifQ._kc"
                    "SHTzcngWIt-LRX6yBx8ftpekT_Dqo8qbPyfgFjSQ"
                ),
            },
        },
    },
)
def refresh_token():
    """Refresh access and refresh tokens

    When access token is expired, call this resource using the refresh token to get a
    new pair of tokens.

    As opposed to all other resources, this resource must be accessed using the refresh
    token, not the access token.
    """
    user = get_current_user()
    return {
        "status": "success",
        "access_token": auth.encode(user).decode("utf-8"),
        "refresh_token": auth.encode(user, token_type="refresh").decode("utf-8"),
    }
