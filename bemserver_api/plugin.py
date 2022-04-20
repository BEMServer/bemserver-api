from bemserver_core.plugin import BEMServerCorePlugin


class BEMServerAPIPlugin(BEMServerCorePlugin):

    #: API blueprint to register under /plugins
    API_BLUEPRINT = None
