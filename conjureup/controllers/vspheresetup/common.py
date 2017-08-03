from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.models.credential import CredentialManager
from conjureup.models.provider import load_schema


class BaseVSphereSetupController:
    def __init__(self):
        cloud = juju.get_cloud(app.current_cloud)

        vsphere_provider = load_schema(app.current_cloud_type)
        credential_manager = CredentialManager(app.current_cloud,
                                               app.current_credential)
        credentials = credential_manager.to_dict()
        credentials.update({'host': cloud['endpoint']})
        vsphere_provider.login(credentials)

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
