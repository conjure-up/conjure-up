from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.controllers.deploy import DeployController
from conjure.juju import Juju
import q


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
        self.config = self.common['config']
        if self.cloud and self.bootstrap:
            self.excerpt = (
                "Please name your new controller")
            self.view = JujuControllerView(self.common,
                                           None,
                                           self.deploy)
        else:
            controllers = Juju.controllers().keys()
            models = {}
            for c in controllers:
                Juju.switch(c)
                models[c] = Juju.models()
            self.excerpt = (
                "Please select the model you wish to deploy to")
            self.view = JujuControllerView(self.common,
                                           models,
                                           self.deploy)

    def deploy(self, controller):
        """ Deploy to juju controller

        Arguments:
        controller: Juju controller to deploy to
        """
        # if self.bootstrap:
        #     Juju.bootstrap(controller, self.cloud)
        # Juju.switch(controller)
        DeployController(self.common, controller).render()

    def render(self):
        self.common['ui'].set_header(
            title="Juju Controller",
            excerpt=self.excerpt
        )
        self.common['ui'].set_body(self.view)
