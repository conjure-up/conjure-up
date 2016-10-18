import json
import os
from collections import defaultdict
from functools import partial
from operator import attrgetter
from subprocess import PIPE

from bundleplacer.assignmenttype import atype_to_label

from conjureup import async, controllers, juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app
from conjureup.telemetry import track_event, track_exception, track_screen
from conjureup.ui.views.app_architecture_view import AppArchitectureView
from conjureup.ui.views.applicationconfigure import ApplicationConfigureView
from conjureup.ui.views.applicationlist import ApplicationListView
from ubuntui.ev import EventLoop


class DeployController:

    def __init__(self):
        self.applications = []
        self.placements = defaultdict(list)
        self.machine_id_map = {}

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

    def do_placement(self, application, sender):
        av = AppArchitectureView(application,
                                 self)
        app.ui.set_header("Architecture")
        app.ui.set_body(av)

    def add_placement(self, application, machine, atype):
        self.placements[machine].append((application, atype))

    def remove_placement(self, application, machine):
        np = []
        np = [(app, at) for app, at in self.placements[machine]
              if app != application]
        self.placements[machine] = np

    def get_placements(self, application, machine):
        return [(app, at) for app, at in self.placements[machine]
                if app == application]

    def get_all_placements(self, application):

        app_placements = []
        for machine, alist in self.placements.items():
            for a, at in alist:
                if a == application:
                    app_placements.append((machine, at))
        return app_placements

    def clear_placements(self, application):
        np = defaultdict(list)
        for m, al in self.placements.items():
            al = [(app, at) for app, at in al if app != application]
            np[m] = al
        self.placements = np

    def handle_sub_view_done(self):
        app.ui.set_header(self.list_header)
        self.list_view.update()
        app.ui.set_body(self.list_view)

    def ensure_machines(self, application, done_cb):
        """add machines if required to fulfill placement directives

        Only useful for maas clouds. others will have no placements
        and this will be a noop.
        """

        # TODO: call tag_names if we haven't yet

        new_machine_list = []
        pending_machines = []
        placements = self.get_all_placements(application)
        for machine, _ in placements:
            if machine not in self.machine_id_map:
                pending_machines.append(machine)
                machine_tag = machine.instance_id.split('/')[-2]
                cons = "tags={}".format(machine_tag)
                machine_attrs = {'series': application.csid.series,
                                 'constraints': cons}
                new_machine_list.append(machine_attrs)
                f = juju.add_machines([machine_attrs])
                result = f.result()
                # TODO here update machine placement map
                self.machine_id_map[machine] = 4747
        done_cb()

    def translate_machine_ids(self, application):
        new_placements = []
        for machine, at in self.get_all_placements(application):
            label = atype_to_label(at)
            plabel = ""
            if label != "":
                plabel += "{}".format(label)
            plabel += str(self.machine_id_map[machine])
            new_placements.append(plabel)
        application.placement_spec = new_placements

    def do_deploy(self, application, msg_cb):
        "launches deploy in background for application"
        self.undeployed_applications.remove(application)

        def msg_both(*args):
            msg_cb(*args)
            app.ui.set_footer(*args)

        def _do_deploy():
            self.translate_machine_ids(application)
            juju.deploy_service(application,
                                app.metadata_controller.series,
                                msg_cb=msg_both,
                                exc_cb=partial(self._handle_exception, "ED"))

        self.ensure_machines(application, _do_deploy)

    def do_deploy_remaining(self):
        "deploys all un-deployed applications"
        def _do_deploy(application):
            self.translate_machine_ids(application)
            juju.deploy_service(application,
                                app.metadata_controller.series,
                                app.ui.set_footer,
                                partial(self._handle_exception, "ED"))

        for application in self.undeployed_applications:
            self.ensure_machines(application,
                                 partial(_do_deploy, application))

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
        juju.add_machines(
            list(app.metadata_controller.bundle.machines.values()),
            exc_cb=partial(self._handle_exception, "ED"))

        self.applications = sorted(app.metadata_controller.bundle.services,
                                   key=attrgetter('service_name'))
        self.undeployed_applications = self.applications[:]

        self.list_view = ApplicationListView(self.applications,
                                             app.metadata_controller,
                                             self)
        self.list_header = "Review and Configure Applications"
        app.ui.set_header(self.list_header)
        app.ui.set_body(self.list_view)


_controller_class = DeployController
