from conjure.ui.views.jujucontroller import JujuControllerView
from conjure.utils import pollinate
from conjure.juju import Juju
from ubuntui.ev import EventLoop
from conjure.models.bundle import BundleModel
from conjure import async
from functools import partial
import os.path as path
import os
from subprocess import check_output
import json


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
        self._post_bootstrap_pollinate = False

    def handle_exception(self, exc):
        pollinate(self.app.session_id, 'EB', self.app.log)
        self.app.ui.show_exception_message(exc)

    def finish(self, controller=None, back=False):
        """ Deploy to juju controller

        Arguments:
        controller: Juju controller to deploy to
        back: if true returns to previous controller
        """
        self.app.log.debug(
            "jujucontroller - selected: {}".format(controller))
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
            pollinate(self.app.session_id, 'J003', self.app.log)

        else:
            self.app.controllers['deploy'].render(self.controller)

    def _handle_bootstrap_done(self, future):
        self.app.log.debug("handle bootstrap")
        result = self._bootstrap_future.result()
        if result.code > 0:
            self.app.log.error(result.errors())
            return self.handle_exception(Exception(result.errors()))
        self._bootstrap_future = None
        pollinate(self.app.session_id, 'J004', self.app.log)
        EventLoop.remove_alarms()
        Juju.switch(self.controller)
        self._post_bootstrap_exec()

    def _post_bootstrap_exec(self):
        """ Executes post-bootstrap.sh if exists
        """
        self._post_bootstrap_sh = path.join('/usr/share/',
                                            self.app.config['name'],
                                            'bundles',
                                            BundleModel.key(),
                                            'post-bootstrap.sh')
        if not path.isfile(self._post_bootstrap_sh) \
           or not os.access(self._post_bootstrap_sh, os.X_OK):
            self.app.log.debug(
                "Unable to execute: {}, skipping".format(
                    self._post_bootstrap_sh))
            return
        self.app.ui.set_footer('Running post-bootstrap tasks.')

        pollinate(self.app.session_id, 'J001', self.app.log)

        self.app.log.debug("post_bootstrap running: {}".format(
            self._post_bootstrap_sh
        ))

        try:
            future = async.submit(partial(check_output,
                                          self._post_bootstrap_sh,
                                          shell=True,
                                          env=self.app.env),
                                  self.handle_exception)
            future.add_done_callback(self._post_bootstrap_done)
        except Exception as e:
            return self.handle_exception(e)

    def _post_bootstrap_done(self, future):
        try:
            result = json.loads(future.result().decode('utf8'))
        except Exception as e:
            self.handle_exception(e)

        self.app.log.debug("pre_bootstrap_done: {}".format(result))
        if result['returnCode'] > 0:
            pollinate(self.app.session_id, 'E001', self.app.log)
            return self.handle_exception(Exception(
                'There was an error during the post '
                'bootstrap processing phase: {}.'.format(result)))
        pollinate(self.app.session_id, 'J002', self.app.log)
        self.app.controllers['deploy'].render(self.controller)

    def render(self, cloud=None, bootstrap=None):
        """ Render controller

        Arguments:
        cloud: defined cloud to use when deploying
        bootstrap: is this a new environment that needs to be bootstrapped
        """

        self.cloud = cloud

        # Set provider type for post-bootstrap
        self.app.env['JUJU_PROVIDERTYPE'] = self.cloud

        self.bootstrap = bootstrap

        if self.cloud and self.bootstrap:
            return self.finish('conjure:default')
        else:
            controllers = Juju.controllers().keys()
            models = {}
            for c in controllers:
                Juju.switch(c)
                models[c] = Juju.models()
            self.view = JujuControllerView(self.app,
                                           models,
                                           self.finish)

        self.app.ui.set_header(
            title="Juju Model",
        )
        self.app.ui.set_body(self.view)
