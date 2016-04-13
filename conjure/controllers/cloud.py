from conjure.ui.views.cloud import CloudView
from conjure.juju import Juju
from conjure.models.bundle import BundleModel
from conjure.utils import pollinate


class CloudController:

    def __init__(self, app):
        self.app = app

    def _list_clouds(self):
        """ Returns list of clouds filtering out any results
        """
        clouds = set(Juju.clouds().keys())

        if BundleModel.whitelist():
            whitelist = set(BundleModel.whitelist())
            return sorted(list(clouds & whitelist))

        elif BundleModel.blacklist():
            blacklist = set(BundleModel.blacklist())
            return sorted(list(clouds ^ blacklist))

        return sorted(list(clouds))

    def finish(self, cloud=None, create_cloud=False, back=False):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        cloud: Cloud to create the controller/model on.
        create_cloud: True/False, if true display create cloud interface
        back: if true loads previous controller
        """
        if back:
            return self.app.controllers['welcome'].render()

        if create_cloud:
            return self.app.controllers['newcloud'].render(cloud)

        pollinate(self.app.session_id, 'CS', self.app.log)

    def render(self):
        self.clouds = self._list_clouds()
        self.config = self.app.config
        self.excerpt = ("Please select from a list of available clouds")
        self.view = CloudView(self.app,
                              self.clouds,
                              self.finish)

        self.app.ui.set_header(
            title="Cloud Providers",
            excerpt=self.excerpt
        )
        self.app.ui.set_body(self.view)
