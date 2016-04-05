from conjure.ui.views.deploy_summary import DeploySummaryView
from conjure.juju import Juju
from functools import partial
from conjure import async
from conjure import shell
from conjure.utils import pollinate
from conjure.models.bundle import BundleModel
import os.path as path


class DeploySummaryController:
    def __init__(self, app):
        self.app = app
        self._pre_exec_sh = path.join('/usr/share/',
                                      self.app.config['name'],
                                      BundleModel.key(),
                                      'pre.sh')
        self._post_exec_sh = path.join('/usr/share/',
                                       self.app.config['name'],
                                       BundleModel.key(),
                                       'post.sh')

    def handle_exception(self, exc):
        pollinate(self.app.session_id, 'EX', self.app.log)
        self.app.ui.show_exception_message(exc)

    def _pre_exec(self):
        """ Executes a bundles pre processing script if exists
        """
        if not path.isfile(self._pre_exec_sh):
            return
        self.app.log("Running pre processing tasks.")
        pollinate(self.app.session_id, 'XA', self.app.log)
        cmd = ("bash {script}".format(script=self._pre_exec_sh))
        future = async.submit(partial(shell, cmd), self.handle_exception)
        future.add_done_callback(self._pre_exec_done)

    def _pre_exec_done(self, future):
        result = future.result()
        if result['returnCode'] > 0:
            raise Exception(
                'There was an error during the pre processing phase.')
        self._deploy_bundle()

    def _deploy_bundle(self):
        """ Performs the bootstrap in between processing scripts
        """
        self.app.log('Deploying bundle')
        pollinate(self.app.session_id, 'DS', self.app.log)
        future = async.submit(
            partial(Juju.deploy_bundle, self.bundle), self.handle_exception)
        future.add_done_callback(self._deploy_bundle_done)

    def _deploy_bundle_done(self, future):
        result = future.result()
        if result['returnCode'] > 0:
            raise Exception(
                'There was an error during the post processing phase.')
        self._post_exec()

    def _post_exec(self):
        """ Executes a bundles post processing script if exists
        """
        if not path.isfile(self._post_exec_sh):
            return
        self.app.log('Perform post processing tasks.')
        pollinate(self.app.session_id, 'XB', self.app.log)
        cmd = ("bash {script}".format(script=self._post_exec_sh))
        future = async.submit(partial(shell, cmd), self.handle_exception)
        future.add_done_callback(self._post_exec_done)

    def _post_exec_done(self, future):
        result = future.result()
        if result['returnCode'] > 0:
            raise Exception(
                'There was an error during the post processing phase.')

    def finish(self, back=False):
        """ Does the actual deployment and loads the summary controller

        Arguments:
        back: If true will go back to previous controller
        """
        if back:
            return self.app.controllers['deploy'].render(
                self.app.current_model
            )
        else:
            self._pre_exec()
            self.app.controllers['finish'].render()

    def render(self, bundle):
        self.bundle = bundle
        self.excerpt = ("Please review the deployment summary before "
                        "proceeding.")
        self.view = DeploySummaryView(self.app,
                                      self.bundle,
                                      self.finish)

        self.app.ui.set_header(
            title="Deploy Summary",
            excerpt=self.excerpt
        )
        self.app.ui.set_body(self.view)
        pollinate(self.app.session_id, 'SS', self.app.log)
