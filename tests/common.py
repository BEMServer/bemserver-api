from contextvars import ContextVar
from contextlib import AbstractContextManager

from bemserver_api.settings import Config


class TestConfig(Config):
    TESTING = True


AUTH_HEADER = ContextVar("auth_header", default=None)


class AuthHeader(AbstractContextManager):
    def __init__(self, creds):
        self.creds = creds

    def __enter__(self):
        self.token = AUTH_HEADER.set("Basic " + self.creds)

    def __exit__(self, *args, **kwargs):
        AUTH_HEADER.reset(self.token)
