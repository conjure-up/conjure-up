from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.controllers.deploy import DeployController
from conjure.juju import Juju


class JujuControllerController:
    def __init__(self, common, cloud=None, bootstrap=False):
        """ init

        Arguments:
        common: common dictionary for conjure
        cloud: defined cloud to use when deploying
        bootstrap: is this a new environment that needs to be bootstrapped
        """
        self.common = common
        self.cloud = cloud
        self.bootstrap = bootstrap
        self.models = Juju.models()
        self.config = self.common['config']
        if self.cloud and self.bootstrap:
            self.excerpt = (
                "Please name your controller")
            self.view = JujuControllerView(self.common,
                                           None,
                                           self.deploy)
        else:
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
        if self.bootstrap:
            Juju.bootstrap(controller, self.cloud)
        Juju.switch(controller)
        DeployController(self.common).render()

    def render(self):
        self.common['ui'].set_header(
            title="Juju Controller",
            excerpt=self.excerpt
        )
        self.common['ui'].set_body(self.view)
