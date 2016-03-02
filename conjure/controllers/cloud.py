from conjure.ui.views.cloud import CloudView
from conjure.controllers.jujucontroller import JujuControllerController
from conjure.juju import Juju


class CloudController:
    def __init__(self, common, clouds):
        self.common = common
        self.clouds = sorted(Juju.clouds().keys())
        self.config = self.common['config']
        self.excerpt = ("Please select from a list of available clouds. ")
        self.view = CloudView(self.common,
                              self.clouds,
                              self.finish)

    def finish(self, cloud):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        cloud: Cloud to create the controller/model on.
        """
        JujuControllerController(self.common, cloud, bootstrap=True).render()

    def render(self):
        self.common['ui'].set_header(
            title="Select a Cloud",
            excerpt=self.excerpt
        )
        self.common['ui'].set_body(self.view)
