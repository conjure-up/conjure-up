from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.juju import Juju


class JujuControllerController:
    def __init__(self, app, cloud=None, bootstrap=False):
        """ init

        Arguments:
        app: common dictionary for conjure
        cloud: defined cloud to use when deploying
        bootstrap: is this a new environment that needs to be bootstrapped
        """
        self.app = app
        self.cloud = cloud
        self.bootstrap = bootstrap
        self.config = self.app.config
        if self.cloud and self.bootstrap:
            self.excerpt = (
                "Please name your new model")
            self.view = JujuControllerView(self.app,
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
            self.view = JujuControllerView(self.app,
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
        self.app.controllers['deploy'](self.app, model).render()

    def render(self):
        self.app.ui.set_header(
            title="Juju Model",
            excerpt=self.excerpt
        )
        self.app.ui.set_body(self.view)
