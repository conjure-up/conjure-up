from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.models.provider import VSphere


class BaseCredentialsController:
    def __init__(self):
        creds = juju.get_credentials().get(app.current_cloud, {})
        creds.pop('default-region', None)

        self.default_credential = creds.pop('default-credential', None)
        self.credentials = sorted(creds.keys())

        if len(self.credentials) == 1:
            self.default_credential = self.credentials[0]

        self.was_picker = False

    def finish(self, cred):
        app.current_credential = cred

        # We need to also attempt to login to the provider as we dont
        # call save_credential.
        # XXX: is this the best approach?
        if app.current_cloud_type == 'vsphere' and \
           not app.vsphere.authenticated:
            vsphere_creds = juju.get_credential(app.current_cloud, cred)
            vsphere_cloud = juju.get_cloud(app.current_cloud)
            vsphere_provider = VSphere()
            vsphere_provider.endpoint.value = vsphere_cloud['endpoint']
            vsphere_provider.user.value = vsphere_creds['user']
            vsphere_provider.password.value = vsphere_creds['password']
            vsphere_provider.login()
        controllers.use('regions').render()
