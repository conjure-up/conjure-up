from conjure.ui.views.cloud import CloudView
from conjure.juju import Juju


class CloudController:

    def __init__(self, app):
        self.app = app
        self.clouds = sorted(Juju.clouds().keys())
        self.config = self.app.config
        self.excerpt = ("Please select from a list of available clouds or "
                        "optionally create a new cloud.")
        self.view = CloudView(self.app,
                              self.clouds,
                              self.finish)

    def finish(self, cloud=None, create_cloud=False, back=False):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        cloud: Cloud to create the controller/model on.
        create_cloud: True/False, if true display create cloud interface
        back: if true loads previous controller
        """
        if back:
            return self.app.controllers['welcome'].render()

        if not create_cloud and cloud is not None:
            self.app.controllers['jujucontroller'].render(
                cloud, bootstrap=True)

    def render(self):
        self.app.ui.set_header(
            title="Cloud Providers",
            excerpt=self.excerpt
        )
        self.app.ui.set_body(self.view)
