import json
import os
from collections import defaultdict
from functools import partial
from operator import attrgetter
from subprocess import PIPE

from bundleplacer.assignmenttype import AssignmentType, atype_to_label
from conjureup import async, controllers, juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app
from conjureup.maas import setup_maas
from conjureup.telemetry import track_event, track_exception, track_screen
from conjureup.ui.views.app_architecture_view import AppArchitectureView
from conjureup.ui.views.applicationconfigure import ApplicationConfigureView
from conjureup.ui.views.applicationlist import ApplicationListView
from ubuntui.ev import EventLoop

DEPLOY_ASYNC_QUEUE = "DEPLOY_ASYNC_QUEUE"


class DeployController:

    def __init__(self):
        self.applications = []
        self.assignments = defaultdict(list)
        self.deployed_juju_machines = {}
        self.maas_machine_map = {}
        self.init_machines_assignments()

    def init_machines_assignments(self):
        """Initialize the controller's machines and assignments.

        If no machines are specified, or we are deploying to a LXD
        controller, add a top-level machine for each app - assumes
        that no placement directives exist in the bundle, and logs any
        it finds.

        Otherwise, syncs assignments from the bundle's applications'
        placement specs.
        """
        bundle = app.metadata_controller.bundle

        if len(bundle.machines) == 0 or app.current_cloud == "localhost":
            self.generate_juju_machines()
        else:
            self.sync_assignments()

    def _handle_exception(self, tag, exc):
        if app.showing_error:
            return
        app.showing_error = True
        track_exception(exc.args[0])
        app.ui.show_exception_message(exc)
        EventLoop.remove_alarms()

    def _pre_deploy_exec(self):
        """ runs pre deploy script if exists
        """
        app.env['JUJU_PROVIDERTYPE'] = model_info().provider_type
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model
        app.env['CONJURE_UP_SPELLSDIR'] = app.argv.spells_dir

        pre_deploy_sh = os.path.join(app.config['spell-dir'],
                                     'steps/00_pre-deploy')
        if os.path.isfile(pre_deploy_sh) \
           and os.access(pre_deploy_sh, os.X_OK):
            track_event("Juju Pre-Deploy", "Started", "")
            msg = "Running pre-deployment tasks."
            app.log.debug(msg)
            app.ui.set_footer(msg)
            out = utils.run(pre_deploy_sh,
                            shell=True,
                            stdout=PIPE,
                            stderr=PIPE,
                            env=app.env)
            try:
                return json.loads(out.stdout.decode())
            except json.decoder.JSONDecodeError:
                app.log.exception(out.stdout.decode())
                app.log.exception(out.stderr.decode())
                raise Exception(out)
        return {'message': 'No pre deploy necessary',
                'returnCode': 0,
                'isComplete': True}

    def _pre_deploy_done(self, future):

        e = future.exception()
        if e:
            self._handle_exception('Pre Deploy', e)
            return

        result = future.result()
        app.log.debug("pre_deploy_done: {}".format(result))

        if result['returnCode'] > 0:
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
        av = AppArchitectureView(application,
                                 self)
        app.ui.set_header(av.header)
        app.ui.set_body(av)

    def generate_juju_machines(self):
        """ Add a separate juju machine for each app.
        Intended for bundles with no machines defined.

        NOTE: assumes there are no placement specs in the bundle.
        """
        bundle = app.metadata_controller.bundle
        midx = 0
        for bundle_application in sorted(bundle.services,
                                         key=attrgetter('service_name')):
            if bundle_application.placement_spec:
                if app.current_cloud == "localhost":
                    app.log.info("Ignoring placement spec because we are "
                                 "deploying to LXD: {}".format(
                                     bundle_application.placement_spec))
                else:
                    app.log.warning("Ignoring placement spec because no "
                                    "machines were set in the "
                                    "bundle: {}".format(
                                        bundle_application.placement_spec))

            for n in range(bundle_application.num_units):
                bundle.add_machine(dict(series=bundle.series),
                                   str(midx))
                self.add_assignment(bundle_application, str(midx),
                                    AssignmentType.DEFAULT)
                midx += 1

    def sync_assignments(self):
        bundle = app.metadata_controller.bundle
        for bundle_application in bundle.services:
            deployargs = bundle_application.as_deployargs()
            spec_list = deployargs.get('placement', [])
            for spec in spec_list:
                juju_machine_id = spec['directive']
                atype = {"lxd": AssignmentType.LXD,
                         "kvm": AssignmentType.KVM,
                         "#": AssignmentType.BareMetal}[spec['scope']]
                self.add_assignment(bundle_application, juju_machine_id, atype)

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

    def clear_machine_pins(self):
        """Remove all mappings between juju machines and maas machines.

        Clears tag constraints that were set when pinning.
        """

        for juju_machine_id, maas_machine in self.maas_machine_map.items():
            bundle = app.metadata_controller.bundle
            juju_machine = bundle.machines[juju_machine_id]
            maas_machine_tag = maas_machine.instance_id.split('/')[-2]
            constraints = juju_machine.get('constraints', '')
            newcons = []

            for con in constraints.split():
                if not con.startswith('tags='):
                    newcons.append(con)
                else:
                    clean_tags = [t for t in con[5:].split(',')
                                  if t != maas_machine_tag]
                    if len(clean_tags) > 0:
                        newcons.append('tags={}'.format(','.join(clean_tags)))

            if len(newcons) > 0:
                juju_machine['constraints'] = ' '.join(newcons)
            else:
                if 'constraints' in juju_machine:
                    del juju_machine['constraints']

        self.maas_machine_map = {}

    def set_machine_pin(self, juju_machine_id, maas_machine):
        """store the mapping between a juju machine and maas machine.


        Also ensure that the juju machine has constraints that
        uniquely id the maas machine

        """
        bundle = app.metadata_controller.bundle
        juju_machine = bundle.machines[juju_machine_id]
        tag = maas_machine.instance_id.split('/')[-2]
        tagstr = "tags={}".format(tag)
        if 'constraints' in juju_machine:
            juju_machine['constraints'] += " " + tagstr
        else:
            juju_machine['constraints'] = tagstr

        self.maas_machine_map[juju_machine_id] = maas_machine

    def apply_assignments(self, application):
        new_assignments = []
        for juju_machine_id, at in self.get_all_assignments(application):
            label = atype_to_label([at])[0]
            plabel = ""
            if label != "":
                plabel += "{}".format(label)
            plabel += self.deployed_juju_machines.get(juju_machine_id,
                                                      juju_machine_id)
            new_assignments.append(plabel)
        application.placement_spec = new_assignments

    def ensure_machines_async(self, application, done_cb):
        """If 'application' is assigned to any machine that haven't been added yet,
        first add the machines then call done_cb
        """
        def _do_ensure_machines():
            if app.current_cloud == 'maas':
                self.ensure_machines_maas(application, done_cb)
            else:
                self.ensure_machines_nonmaas(application, done_cb)

        async.submit(_do_ensure_machines,
                     partial(self._handle_exception,
                             "Error while adding machines"),
                     queue_name=DEPLOY_ASYNC_QUEUE)

    def ensure_machines_maas(self, application, done_cb):
        app_placements = self.get_all_assignments(application)
        for juju_machine_id in [j_id for j_id, _ in app_placements
                                if j_id not in self.deployed_juju_machines]:
            machine_attrs = {'series': application.csid.series}

            if juju_machine_id in self.maas_machine_map:
                maas_machine = self.maas_machine_map[juju_machine_id]
                app.maas.client.assign_id_tags([maas_machine])
                machine_tag = maas_machine.instance_id.split('/')[-2]
                cons = "tags={}".format(machine_tag)
                machine_attrs['constraints'] = cons

            f = juju.add_machines([machine_attrs],
                                  msg_cb=app.ui.set_footer,
                                  exc_cb=partial(self._handle_exception,
                                                 "Error Adding Machine"))
            add_machines_result = f.result()
            self._handle_add_machines_return(juju_machine_id,
                                             add_machines_result)
        done_cb()

    def ensure_machines_nonmaas(self, application, done_cb):
        juju_machines = app.metadata_controller.bundle.machines
        app_placements = self.get_all_assignments(application)
        for juju_machine_id in [j_id for j_id, _ in app_placements
                                if j_id not in self.deployed_juju_machines]:
            juju_machine = juju_machines[juju_machine_id]
            f = juju.add_machines([juju_machine],
                                  msg_cb=app.ui.set_footer,
                                  exc_cb=partial(self._handle_exception,
                                                 "Error Adding Machine"))
            result = f.result()
            self._handle_add_machines_return(juju_machine_id, result)
        done_cb()

    def _handle_add_machines_return(self, juju_machine_id, new_machine_ids):
        if len(new_machine_ids) != 1:
            raise Exception("Unexpected return value from "
                            "add_machines: {}".format(new_machine_ids))
        new_machine_id = new_machine_ids[0]
        self.deployed_juju_machines[juju_machine_id] = new_machine_id

    def _do_deploy_one(self, application, msg_cb):
        self.apply_assignments(application)
        juju.deploy_service(application,
                            app.metadata_controller.series,
                            msg_cb=msg_cb,
                            exc_cb=partial(self._handle_exception, "ED"))

    def do_deploy(self, application, msg_cb):
        "launches deploy in background for application"
        self.undeployed_applications.remove(application)

        def msg_both(*args):
            msg_cb(*args)
            app.ui.set_footer(*args)

        self.ensure_machines_async(application, partial(self._do_deploy_one,
                                                        application, msg_both))

    def do_deploy_remaining(self):
        "deploys all un-deployed applications"

        for application in self.undeployed_applications:
            self.ensure_machines_async(application,
                                       partial(self._do_deploy_one,
                                               application,
                                               app.ui.set_footer))

    def finish(self):
        def enqueue_set_relations():
            rel_future = juju.set_relations(self.applications,
                                            app.ui.set_footer,
                                            partial(self._handle_exception,
                                                    "Error setting relations"))
            return rel_future
        f = async.submit(enqueue_set_relations,
                         partial(self._handle_exception,
                                 "Error setting relations"),
                         queue_name=DEPLOY_ASYNC_QUEUE)

        if app.bootstrap.running and not app.bootstrap.running.done():
            return controllers.use('bootstrapwait').render(f)
        else:
            return controllers.use('deploystatus').render(f)

    def render(self):
        # If bootstrap fails fast, we may be called after the error
        # screen was already shown. We should bail to avoid
        # overwriting the error screen.
        bf = app.bootstrap.running
        if bf and bf.done() and bf.exception():
            return

        track_screen("Deploy")
        try:
            future = async.submit(self._pre_deploy_exec,
                                  partial(self._handle_exception, 'E003'),
                                  queue_name=juju.JUJU_ASYNC_QUEUE)
            if future:
                future.add_done_callback(self._pre_deploy_done)
        except Exception as e:
            return self._handle_exception('E003', e)

        self.applications = sorted(app.metadata_controller.bundle.services,
                                   key=attrgetter('service_name'))
        self.undeployed_applications = self.applications[:]

        if app.current_cloud == 'maas':
            def try_setup_maas():
                """Try to init maas client.
                loops until we get an unexpected exception or we succeed.
                """
                n = 30
                while True:
                    try:
                        setup_maas()
                    except juju.ControllerNotFoundException as e:
                        async.sleep_until(1)
                        n -= 1
                        if n == 0:
                            raise e
                        continue
                    else:
                        break

            async.submit(try_setup_maas,
                         partial(self._handle_exception, 'EM'))

        self.list_view = ApplicationListView(self.applications,
                                             app.metadata_controller,
                                             self)
        self.list_header = "Review and Configure Applications"
        app.ui.set_header(self.list_header)
        app.ui.set_body(self.list_view)


_controller_class = DeployController
