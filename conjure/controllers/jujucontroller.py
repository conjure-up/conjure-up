from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.juju import Juju
from conjure.async import AsyncPool
from functools import partial


class JujuControllerController:
    def __init__(self, app):
        """ init

        Arguments:
        app: common dictionary for conjure
        """
        self.app = app
        self.cloud = None
        self.bootstrap = None

    def finish(self, controller=None, back=False):
        """ Deploy to juju controller

        Arguments:
        controller: Juju controller to deploy to
        back: if true returns to previous controller
        """
        if back:
            return self.app.controllers['welcome'].render()

        if self.bootstrap:
            # FIXME: Once admin/default models exist in juju
            AsyncPool.submit(
                partial(Juju.bootstrap, 'conjure', self.cloud))

        Juju.switch(controller)
        self.app.controllers['deploy'].render(controller)

    def render(self, cloud=None, bootstrap=None):
        """ Render controller

        Arguments:
        cloud: defined cloud to use when deploying
        bootstrap: is this a new environment that needs to be bootstrapped
        """

        self.cloud = cloud
        self.bootstrap = bootstrap

        if self.cloud and self.bootstrap:
            # FIXME: Once admin/default models exist in juju
            return self.finish('conjure:conjure')
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
                                           self.finish)

        self.app.ui.set_header(
            title="Juju Model",
            excerpt=self.excerpt
        )
        self.app.ui.set_body(self.view)
