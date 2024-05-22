from contextlib import AbstractContextManager
from contextvars import ContextVar

from bemserver_api.extensions.authentication import auth, jwt
from bemserver_api.settings import Config


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "Test secret"
    AUTH_METHODS = [
        "Bearer",
        "Basic",
    ]


AUTH_HEADER = ContextVar("auth_header", default=None)


class AuthHeader(AbstractContextManager):
    def __init__(self, creds):
        self.creds = creds

    def __enter__(self):
        self.token = AUTH_HEADER.set(self.creds)

    def __exit__(self, *args, **kwargs):
        AUTH_HEADER.reset(self.token)


def make_token(user_email, token_type):
    # Make an access token with no expiration
    return jwt.encode(
        auth.HEADER.copy(),
        {"email": user_email, "type": token_type},
        TestConfig.SECRET_KEY,
    ).decode()
