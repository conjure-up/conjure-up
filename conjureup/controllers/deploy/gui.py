import q

import json
import os
from collections import defaultdict
from functools import partial
from operator import attrgetter
from subprocess import PIPE

from bundleplacer.assignmenttype import atype_to_label, AssignmentType

from conjureup import async, controllers, juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app
from conjureup.maas import setup_maas
from conjureup.telemetry import track_event, track_exception, track_screen
from conjureup.juju import get_controller_info
from conjureup.ui.views.app_architecture_view import AppArchitectureView
from conjureup.ui.views.applicationconfigure import ApplicationConfigureView
from conjureup.ui.views.applicationlist import ApplicationListView
from ubuntui.ev import EventLoop


class DeployController:

    def __init__(self):
        self.applications = []
        self.assignments = defaultdict(list)
        self.maas_machine_map = {}
        c_info = get_controller_info(app.current_controller)
        self.cloud_type = c_info['details']['cloud']

    def _handle_exception(self, tag, exc):
        track_exception(exc.args[0])
        app.ui.show_exception_message(exc)
        self.showing_error = True
        EventLoop.remove_alarms()

    def _pre_deploy_exec(self):
        """ runs pre deploy script if exists
        """
        app.env['JUJU_PROVIDERTYPE'] = model_info(
            app.current_model)['provider-type']
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model

        pre_deploy_sh = os.path.join(app.config['spell-dir'],
                                     'steps/00_pre-deploy')
        if os.path.isfile(pre_deploy_sh) \
           and os.access(pre_deploy_sh, os.X_OK):
            track_event("Juju Pre-Deploy", "Started", "")
            msg = "Running pre-deployment tasks."
            app.log.debug(msg)
            app.ui.set_footer(msg)
            return utils.run(pre_deploy_sh,
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
            track_exception("Pre-deploy error")
            return self._handle_exception('E003', Exception(
                'There was an error during the pre '
                'deploy processing phase: {}.'.format(result)))
        else:
            app.ui.set_footer("Pre-deploy processing done.")

    def do_configure(self, application, sender):
        "shows configure view for application"
        cv = ApplicationConfigureView(application,
                                      app.metadata_controller,
                                      self)
        app.ui.set_header("Configure {}".format(application.service_name))
        app.ui.set_body(cv)

    def do_architecture(self, application, sender):

        # TODO - do we really always want to do this?

        # If no machines are specified, add a machine for each app:
        bundle = app.metadata_controller.bundle
        if len(bundle.machines) == 0:
            self.generate_juju_machines()

        av = AppArchitectureView(application,
                                 self)
        app.ui.set_header(av.header)
        app.ui.set_body(av)

    def generate_juju_machines(self):
        """ Add a separate juju machine for each app.
        Intended for bundles with no machines defined.
        """
        bundle = app.metadata_controller.bundle
        midx = 0
        for bundle_application in bundle.services:
            for n in range(bundle_application.num_units):
                bundle.add_machine(dict(series=bundle.series),
                                   str(midx))
                self.add_assignment(bundle_application, str(midx),
                                    AssignmentType.DEFAULT)
                midx += 1

    def add_assignment(self, application, juju_machine_id, atype):
        self.assignments[juju_machine_id].append((application, atype))

    def remove_assignment(self, application, machine):
        np = []
        np = [(app, at) for app, at in self.assignments[machine]
              if app != application]
        self.assignments[machine] = np

    def get_assignments(self, application, machine):
        return [(app, at) for app, at in self.assignments[machine]
                if app == application]

    def get_all_assignments(self, application):

        app_assignments = []
        for juju_machine_id, alist in self.assignments.items():
            for a, at in alist:
                if a == application:
                    app_assignments.append((juju_machine_id, at))
        return app_assignments

    def clear_assignments(self, application):
        np = defaultdict(list)
        for m, al in self.assignments.items():
            al = [(app, at) for app, at in al if app != application]
            np[m] = al
        self.assignments = np

    def handle_sub_view_done(self):
        app.ui.set_header(self.list_header)
        self.list_view.update()
        app.ui.set_body(self.list_view)

    def set_machine_pin(self, juju_machine_id, maas_machine_id):
        """store the mapping between a juju machine and maas machine.

        Also ensure that the juju machine has constraints that
        uniquely id the maas machine

        """
        bundle = app.metadata_controller.bundle
        juju_machine = bundle.machines[juju_machine_id]
        tagstr = "tags={}".format(maas_machine_id)
        if 'constraints' in juju_machine:
            juju_machine['constraints'] += "," + tagstr
        else:
            juju_machine['constraints'] = tagstr

        self.maas_machine_map[juju_machine_id] = maas_machine_id

    def apply_assignments(self, application):
        new_assignments = []
        for juju_machine_id, at in self.get_all_assignments(application):
            label = atype_to_label([at])[0]
            plabel = ""
            if label != "":
                plabel += "{}".format(label)
            plabel += juju_machine_id
            new_assignments.append(plabel)
        application.placement_spec = new_assignments

    def do_deploy(self, application, msg_cb):
        "launches deploy in background for application"
        self.undeployed_applications.remove(application)

        def msg_both(*args):
            msg_cb(*args)
            app.ui.set_footer(*args)

        self.apply_assignments(application)
        juju.deploy_service(application,
                            app.metadata_controller.series,
                            msg_cb=msg_both,
                            exc_cb=partial(self._handle_exception, "ED"))

    def do_deploy_remaining(self):
        "deploys all un-deployed applications"

        for application in self.undeployed_applications:
            self.apply_assignments(application)
            juju.deploy_service(application,
                                app.metadata_controller.series,
                                app.ui.set_footer,
                                partial(self._handle_exception, "ED"))

    def finish(self):
        juju.set_relations(self.applications,
                           app.ui.set_footer,
                           partial(self._handle_exception, "ED"))

        if app.bootstrap.running and not app.bootstrap.running.done():
            return controllers.use('bootstrapwait').render()
        else:
            return controllers.use('deploystatus').render()

    def render(self):
        track_screen("Deploy")
        try:
            future = async.submit(self._pre_deploy_exec,
                                  partial(self._handle_exception, 'E003'),
                                  queue_name=juju.JUJU_ASYNC_QUEUE)
            future.add_done_callback(self._pre_deploy_done)
        except Exception as e:
            return self._handle_exception('E003', e)

        #  TODO - maybe don't do this here for MAAS?
        # juju.add_machines(
        #     list(app.metadata_controller.bundle.machines.values()),
        #     exc_cb=partial(self._handle_exception, "ED"))

        self.applications = sorted(app.metadata_controller.bundle.services,
                                   key=attrgetter('service_name'))
        self.undeployed_applications = self.applications[:]

        if self.cloud_type == 'maas':
            setup_maas()

        self.list_view = ApplicationListView(self.applications,
                                             app.metadata_controller,
                                             self)
        self.list_header = "Review and Configure Applications"
        app.ui.set_header(self.list_header)
        app.ui.set_body(self.list_view)


_controller_class = DeployController
