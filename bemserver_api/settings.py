"""Default configuration"""


class Config:
    """Default configuration"""

    # SQLAlchemy parameters
    SQLALCHEMY_DATABASE_URI = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API parameters
    API_TITLE = "BEMServer API"
    API_VERSION = 0.1
    OPENAPI_VERSION = '3.0.2'
    OPENAPI_JSON_PATH = "api-spec.json"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_REDOC_PATH = "/"
    OPENAPI_REDOC_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
