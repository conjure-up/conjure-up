from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.juju import Juju
from ubuntui.ev import EventLoop
import logging

log = logging.getLogger('jujucontroller')


class JujuControllerController:
    def __init__(self, app):
        """ init

        Arguments:
        app: common dictionary for conjure
        """
        self.app = app
        self.cloud = None
        self.bootstrap = None
        self._bootstrap_future = None

    def handle_exception(self, exc):
        self.app.ui.show_exception_message(exc)

    def finish(self, controller=None, back=False):
        """ Deploy to juju controller

        Arguments:
        controller: Juju controller to deploy to
        back: if true returns to previous controller
        """
        self.controller = controller

        if back:
            return self.app.controllers['welcome'].render()

        if self.bootstrap:
            self._bootstrap_future = Juju.bootstrap_async(
                'conjure',
                self.cloud,
                exc_cb=self.handle_exception)
            self._bootstrap_future.add_done_callback(
                self._handle_bootstrap_done)

            self.app.controllers['bootstrapwait'].render()
        else:
            self.app.controllers['deploy'].render(self.controller)

    def _handle_bootstrap_done(self, future):
        result = self._bootstrap_future.result()
        log.debug(result)
        self._bootstrap_future = None

        EventLoop.remove_alarms()
        Juju.switch(self.controller)
        self.app.controllers['deploy'].render(self.controller)

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
