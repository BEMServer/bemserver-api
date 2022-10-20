"""About resources"""
import bemserver_core
import bemserver_api
from bemserver_api import Blueprint

from .schemas import AboutSchema


blp = Blueprint(
    "About", __name__, url_prefix="/about", description="Informations about BEMServer"
)


@blp.get("/")
@blp.etag
@blp.response(200, AboutSchema)
def about():
    """Provide information about BEMServer

    Returns bemserver_core and bemserver_api versions.
    """
    return {
        "versions": {
            "bemserver_core": bemserver_core.__version__,
            "bemserver_api": bemserver_api.__version__,
        }
    }
