import asyncio
from collections import defaultdict
from operator import attrgetter

from bundleplacer.assignmenttype import AssignmentType, atype_to_label

from conjureup import controllers, events, juju
from conjureup.app_config import app
from conjureup.maas import setup_maas
from conjureup.telemetry import track_screen
from conjureup.ui.views.app_architecture_view import AppArchitectureView
from conjureup.ui.views.applicationconfigure import ApplicationConfigureView
from conjureup.ui.views.applicationlist import ApplicationListView

from . import common


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

    async def get_maas_constraints(self, machine_id):
        if machine_id not in self.maas_machine_map:
            return ''
        maas_machine = self.maas_machine_map[machine_id]
        await app.loop.run_in_executor(
            None, app.maas.client.assign_id_tags, [maas_machine])
        machine_tag = maas_machine.instance_id.split('/')[-2]
        return "tags={}".format(machine_tag)

    async def ensure_machines(self, application):
        """If 'application' is assigned to any machine that haven't been added yet,
        add the machines prior to deployment.
        """
        cloud_type = juju.get_cloud_types_by_name()[app.current_cloud]

        if cloud_type == 'maas':
            await events.MAASConnected.wait()
        app_placements = self.get_all_assignments(application)
        juju_machines = app.metadata_controller.bundle.machines
        machines = {}
        for virt_machine_id, _ in app_placements:
            if virt_machine_id in self.deployed_juju_machines:
                continue
            machine_attrs = {
                'series': application.csid.series,
            }
            if cloud_type == 'maas':
                machine_attrs['constraints'] = \
                    await self.get_maas_constraints(virt_machine_id)
            else:
                machine_attrs.update(juju_machines[virt_machine_id])
            machines[virt_machine_id] = machine_attrs

        return await juju.add_machines([application], machines,
                                       msg_cb=app.ui.set_footer)

    async def _do_deploy(self, application, msg_cb):
        "launches deploy in background for application"
        if application not in self.undeployed_applications:
            app.log.error('Skipping attempt to deploy unavailable '
                          '{}'.format(application))
            return
        self.undeployed_applications.remove(application)

        default_series = app.metadata_controller.series

        added_machines = await self.ensure_machines(application)

        for virt_machine_id, real_machine_id in added_machines.items():
            self.deployed_juju_machines[virt_machine_id] = real_machine_id
        self.apply_assignments(application)

        await juju.deploy_service(application, default_series, msg_cb=msg_cb)
        await juju.set_relations(application, msg_cb=app.ui.set_footer)

    def do_deploy(self, application, msg_cb):
        def msg_both(*args):
            msg_cb(*args)
            app.ui.set_footer(*args)

        app.loop.create_task(self._do_deploy(application, msg_both))

    def do_deploy_remaining(self):
        "deploys all un-deployed applications"
        for application in self.undeployed_applications:
            app.loop.create_task(self._do_deploy(application,
                                                 app.ui.set_footer))

    def sync_assignment_opts(self):
        svc_opts = {}
        for application in self.applications:
            svc_opts[application.service_name] = application.options

        for mid, al in self.assignments.items():
            for svc, _ in al:
                svc.options = svc_opts[svc.service_name]

    async def connect_maas(self):
        """Try to init maas client.
        loops until we get an unexpected exception or we succeed.
        """
        n = 30
        while True:
            try:
                await app.loop.run_in_executor(None, setup_maas)
            except juju.ControllerNotFoundException as e:
                await asyncio.sleep(1)
                n -= 1
                if n == 0:
                    raise e
                continue
            else:
                events.MAASConnected.set()
                break

    async def watch_for_deploy_complete(self):
        await asyncio.gather(*(events.RelationsAdded.wait(a.service_name)
                               for a in self.applications))
        events.DeploymentComplete.set()
        if not events.ModelSettled.is_set():
            app.ui.set_footer('Applications deployed and related, '
                              'waiting for everything to become ready.')

    def finish(self):
        app.loop.create_task(self.watch_for_deploy_complete())

        self.sync_assignment_opts()
        common.write_bundle(self.assignments)

        if app.current_controller in juju.get_controllers()['controllers']:
            events.Bootstrapped.set()
            app.loop.create_task(juju.add_model(app.current_model,
                                                app.current_controller,
                                                app.current_cloud))
            return controllers.use('deploystatus').render()
        else:
            return controllers.use('bootstrap').render()

    def render(self):
        # If bootstrap fails fast, we may be called after the error
        # screen was already shown. We should bail to avoid
        # overwriting the error screen.
        if events.Error.is_set():
            return

        track_screen("Deploy")
        app.loop.create_task(common.pre_deploy(app.ui.set_footer))

        self.applications = sorted(app.metadata_controller.bundle.services,
                                   key=attrgetter('service_name'))
        self.undeployed_applications = self.applications[:]

        cloud_type = juju.get_cloud_types_by_name()[app.current_cloud]
        if cloud_type == 'maas':
            app.loop.create_task(self.connect_maas())

        self.list_view = ApplicationListView(self.applications,
                                             app.metadata_controller,
                                             self)
        self.list_header = "Review and Configure Applications"
        app.ui.set_header(self.list_header)
        app.ui.set_body(self.list_view)


_controller_class = DeployController
