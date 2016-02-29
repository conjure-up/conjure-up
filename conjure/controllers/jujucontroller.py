from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.controllers.deploy import DeployController
from conjure.juju import Juju


class JujuControllerController:
    def __init__(self, common, cloud=None):
        self.common = common
        self.cloud = cloud
        self.models = Juju.models()
        self.config = self.common['config']
        self.excerpt = (
            "Please select the controller:model you wish to deploy to")
        self.view = JujuControllerView(self.common,
                                       self.models,
                                       self.deploy)

    def deploy(self, controller):
        """ Deploy to juju controller

        Arguments:
        controller: Juju controller to deploy to
        """
        Juju.switch(controller)
        DeployController(self.common, controller).render()

    def render(self):
        self.common['ui'].set_header(
            title="Juju Controller",
            excerpt=self.excerpt
        )
        self.common['ui'].set_body(self.view)
