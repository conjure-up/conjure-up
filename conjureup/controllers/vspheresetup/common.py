from conjureup import controllers
from conjureup.app_config import app


class VSphereRegionError(Exception):
    pass


class BaseVSphereSetupController:
    def finish(self, data):
        app.provider.model_defaults = {
            'primary-network': data['primary-network'],
            'external-network': data['external-network'],
            'datastore': data['datastore']
        }
        return controllers.use('controllerpicker').render()
