import asyncio

from conjureup import controllers
from conjureup.app_config import app


class BaseVSphereSetupController:
    def __init__(self):
        self.authenticating = asyncio.Event()

    def finish(self, data):
        app.provider.model_defaults = {
            'primary-network': data['primary-network'],
            'external-network': data['external-network'],
            'datastore': data['datastore']
        }
        return controllers.use('controllerpicker').render()
