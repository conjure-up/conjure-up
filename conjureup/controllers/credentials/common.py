from conjureup import controllers, juju
from conjureup.app_config import app


class BaseCredentialsController:
    def load_credentials(self):
        creds = juju.get_credentials().get(app.provider.cloud, {})
        creds.pop('default-region', None)

        default_credential = creds.pop('default-credential', None)
        self.credentials = sorted(creds.keys())

        if len(self.credentials) == 1:
            default_credential = self.credentials[0]

        if not app.provider.credential:
            app.provider.credential = default_credential

        self.was_picker = False

    def finish(self):
        controllers.use('regions').render()
