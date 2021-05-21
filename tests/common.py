from bemserver_api.settings import Config


class TestConfig(Config):
    TESTING = True
    AUTH_ENABLED = False
