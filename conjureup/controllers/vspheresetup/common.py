from conjureup import controllers
from conjureup.app_config import app


class BaseVSphereSetupController:
    def __init__(self):
        # Assign current datacenter
        for dc in app.vsphere.client.get_datacenters():
            if dc.name == app.current_region:
                self.datacenter = dc

    def finish(self, data):
        app.current_model_defaults = {
            'primary-network': data['primary-network'],
            'external-network': data['external-network'],
            'datastore': data['datastore']
        }
        return controllers.use('controllerpicker').render()
