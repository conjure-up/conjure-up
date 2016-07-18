from functools import partial
import json
import os
from ubuntui.ev import EventLoop
from subprocess import run, PIPE
from conjure import controllers
from conjure import juju
from conjure import async
from conjure.app_config import app
from conjure.ui.views.service_walkthrough import ServiceWalkthroughView
from conjure import utils
from conjure.api.models import model_info
from .common import get_bundleinfo, get_metadata_controller


class DeployController:

    def __init__(self):
        self.bundle_filename = None
        self.bundle = None
        self.services = []
        self.svc_idx = 0
        self.showing_error = False
        self.is_predeploy_queued = False

    def _handle_exception(self, tag, exc):
        utils.pollinate(app.session_id, tag)
        app.ui.show_exception_message(exc)
        self.showing_error = True
        EventLoop.remove_alarms()

    def _pre_deploy_exec(self):
        """ runs pre deploy script if exists
        """
        self.is_predeploy_queued = True
        app.env['JUJU_PROVIDERTYPE'] = model_info(
            juju.get_current_model())['provider-type']

        pre_deploy_sh = os.path.join(app.config['spell-dir'],
                                     'conjure/steps/00_pre-deploy')
        if os.path.isfile(pre_deploy_sh) \
           and os.access(pre_deploy_sh, os.X_OK):
            utils.pollinate(app.session_id, 'J001')
            msg = "Running pre-deployment tasks."
            app.log.debug(msg)
            app.ui.set_footer(msg)
            return run(pre_deploy_sh,
                       shell=True,
                       stdout=PIPE,
                       stderr=PIPE,
                       env=app.env)
        return json.dumps({'message': 'No pre deploy necessary',
                           'returnCode': 0,
                           'isComplete': True})

    def _pre_deploy_done(self, future):
        try:
            result = json.loads(future.result().stdout.decode())
        except AttributeError:
            result = json.loads(future.result())
        except:
            return self._handle_exception(
                'E003',
                Exception(
                    "Problem with pre-deploy: \n{}, ".format(
                        future.result())))

        app.log.debug("pre_deploy_done: {}".format(result))
        if result['returnCode'] > 0:
            utils.pollinate(app.session_id, 'E003')
            return self._handle_exception('E003', Exception(
                'There was an error during the pre '
                'deploy processing phase: {}.'.format(result)))
        else:
            app.ui.set_footer("Pre-deploy processing done.")

    def _do_add_machines(self):
        juju.add_machines([md for _, md in self.bundle.machines.items()],
                          exc_cb=partial(self._handle_exception, "ED"))

    def finish(self, single_service=None):
        """handles deployment

        Arguments:

        single_service: a dict for the service that was just
        configured. finish will schedule a deploy for it and
        call render() again to display the next one.

        if service is None, schedules deploys for all remaining services,
        schedules relations, then continues to next controller

        """
        if single_service:
            juju.deploy_service(single_service,
                                app.ui.set_footer,
                                partial(self._handle_exception, "ED"))
            self.svc_idx += 1
            return self.render()
        else:
            for service in self.services[self.svc_idx:]:
                juju.deploy_service(service,
                                    app.ui.set_footer,
                                    partial(self._handle_exception, "ED"))

            juju.set_relations(self.services,
                               app.ui.set_footer,
                               partial(self._handle_exception, "ED"))

            if app.bootstrap.running and not app.bootstrap.running.done():
                return controllers.use('bootstrapwait').render()
            else:
                return controllers.use('deploystatus').render()

        utils.pollinate(app.session_id, 'PC')

    def render(self):
        if not self.is_predeploy_queued:
            try:
                future = async.submit(self._pre_deploy_exec,
                                      partial(self._handle_exception, 'E003'),
                                      queue_name=juju.JUJU_ASYNC_QUEUE)
                future.add_done_callback(self._pre_deploy_done)
            except Exception as e:
                return self._handle_exception('E003', e)

        if self.showing_error:
            return

        if not self.bundle:
            self.bundle_filename, self.bundle, self.services = get_bundleinfo()

            async.submit(self._do_add_machines,
                         partial(self._handle_exception, "ED"),
                         queue_name=juju.JUJU_ASYNC_QUEUE)

        if not app.metadata_controller:
            app.metadata_controller = get_metadata_controller(
                self.bundle, self.bundle_filename)

        n_total = len(self.services)
        if self.svc_idx >= n_total:
            return self.finish()

        service = self.services[self.svc_idx]
        wv = ServiceWalkthroughView(service, self.svc_idx, n_total,
                                    app.metadata_controller, self.finish)

        app.ui.set_header("Review and Configure Applications")
        app.ui.set_body(wv)

_controller_class = DeployController
