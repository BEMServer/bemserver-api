"""Default configuration"""


class Config:
    """Default configuration"""

    # SQLAlchemy parameters
    SQLALCHEMY_DATABASE_URI = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API parameters
    API_TITLE = "BEMServer API"
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_RAPIDOC_PATH = "/"
    OPENAPI_RAPIDOC_URL = "https://cdn.jsdelivr.net/npm/rapidoc/dist/rapidoc-min.js"
    OPENAPI_RAPIDOC_CONFIG = {
        "theme": "dark",
        "show-header": "false",
        "render-style": "focused",
    }
