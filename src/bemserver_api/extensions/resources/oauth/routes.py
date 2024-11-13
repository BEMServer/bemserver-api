"""Oauth resources"""

import requests

from bemserver_api import Blueprint
from bemserver_api.extensions.authentication import auth

from .schemas import OauthGetJWTArgsSchema, OauthGetJWTRespSchema

blp = Blueprint(
    "Oauth",
    __name__,
    url_prefix="/oauth",
    description="Oauth operations",
)


@blp.route("/")
@blp.arguments(OauthGetJWTArgsSchema)
# @blp.response(
@blp.alt_response(
    200,
    OauthGetJWTRespSchema,
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
def get_token(args):
    """Get JWT token using OAuth"""
    # TODO OAuth class
    return redirect(
        f"https://github.com/login/oauth/authorize?client_id={os.environ.get('GITHUB_CLIENT_ID')}"
    )


@blp.route("/callback")
@blp.arguments(OauthGetJWTArgsSchema)
def callback(args):
    # TODO OAuth class get_token
    params = {
        "client_id": os.environ.get("GITHUB_CLIENT_ID"),
        "client_secret": os.environ.get("GITHUB_CLIENT_SECRET"),
        "code": args["code"],
    }
    try:
        response = requests.post(
            "https://github.com/login/oauth/access_token", json=params
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")
    except Exception as e:
        print(f"Error fetching token: {e}")

    # TODO Oauth class get user
    headers = {"Authorization": f"token {access_token}"}
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        response.raise_for_status()
        user_info = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching user info: {e}")

    return {
        "status": "success",
        "access_token": auth.encode(user).decode("utf-8"),
        "refresh_token": auth.encode(user, token_type="refresh").decode("utf-8"),
    }
