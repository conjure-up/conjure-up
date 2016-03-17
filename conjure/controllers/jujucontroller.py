from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.controllers.deploy import DeployController
from conjure.juju import Juju
import q  # noqa


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
                "Please name your new model")
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

    def deploy(self, controller, default_model=None):
        """ Deploy to juju controller

        Arguments:
        controller: Juju controller to deploy to
        default_model: Optional name to give the default model
        """
        if self.bootstrap:
            Juju.bootstrap(controller, self.cloud)

        model = ""
        if default_model is None:
            model = "{}:default".format(controller)
            Juju.switch(model)
        else:
            model = "{}:{}".format(controller, default_model)
            Juju.switch(model)
        DeployController(self.common, model).render()

    def render(self):
        self.common['ui'].set_header(
            title="Juju Model",
            excerpt=self.excerpt
        )
        self.common['ui'].set_body(self.view)
