"""Default configuration"""


class Config:
    """Default configuration"""

    # Authentication
    SECRET_KEY = ""
    AUTH_METHODS = [
        "Bearer",
    ]

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
        "allow-spec-file-download": "true",
        "show-components": "true",
    }

    # Profiling
    PROFILE_DIR = ""
