from bemserver_api.plugin import BEMServerAPIPlugin

from .model import AUTH_MODEL_CLASSES, AUTH_POLAR_FILES
from .resources import blp


class TestPlugin(BEMServerAPIPlugin):

    AUTH_MODEL_CLASSES = AUTH_MODEL_CLASSES
    AUTH_POLAR_FILES = AUTH_POLAR_FILES
    API_BLUEPRINT = blp
