from conjureup import controllers
from conjureup.app_config import app


class BaseVSphereSetupController:
    def __init__(self):
        # Assign current datacenter
        app.provider.login()
        for dc in app.provider.client.get_datacenters():
            if dc.name == app.provider.region:
                self.datacenter = dc

    def finish(self, data):
        app.provider.model_defaults = {
            'primary-network': data['primary-network'],
            'external-network': data['external-network'],
            'datastore': data['datastore']
        }
        return controllers.use('controllerpicker').render()
