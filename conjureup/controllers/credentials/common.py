from conjureup import controllers, juju
from conjureup.app_config import app


class BaseCredentialsController:
    def __init__(self):
        self.credentials = juju.get_credentials().get(app.provider.cloud,
                                                      {}).keys()
        app.provider.credential = juju.get_credential(app.provider.cloud, None)
        self.was_picker = False

    def finish(self):
        controllers.use('regions').render()
