import asyncio
from collections import defaultdict
from operator import attrgetter

from bundleplacer.assignmenttype import AssignmentType, atype_to_label

from conjureup import controllers, events, juju
from conjureup.app_config import app
from conjureup.consts import cloud_types
from conjureup.maas import setup_maas
from conjureup.ui.views.app_architecture_view import AppArchitectureView
from conjureup.ui.views.applicationconfigure import ApplicationConfigureView
from conjureup.ui.views.applicationlist import ApplicationListView

from . import common


class ConfigAppsController:

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

        if len(bundle.machines) == 0:
            self.generate_juju_machines()
        else:
            self.sync_assignments()

    def do_configure(self, application):
        "shows configure view for application"
        cv = ApplicationConfigureView(application,
                                      lambda: self.render(going_back=True))
        cv.show()

    def do_architecture(self, application):
        av = AppArchitectureView(application,
                                 self,
                                 lambda: self.render(going_back=True))
        av.show()

    def generate_juju_machines(self):
        """ Add a separate juju machine for each app.
        Intended for bundles with no machines defined.

        NOTE: assumes there are no placement specs in the bundle.
        """
        bundle = app.metadata_controller.bundle
        midx = 0
        for bundle_application in sorted(bundle.services,
                                         key=attrgetter('service_name')):
            for n in range(bundle_application.num_units):
                machine = {'series': bundle.series}
                if bundle_application.constraints:
                    machine['constraints'] = bundle_application.constraints
                bundle.add_machine(machine, str(midx))
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
        """Ensure that the given application has a machine definition.
        """
        if app.provider.cloud_type == cloud_types.MAAS:
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
            if app.provider.cloud_type == cloud_types.MAAS:
                machine_attrs['constraints'] = \
                    await self.get_maas_constraints(virt_machine_id)
            else:
                machine_attrs.update(juju_machines[virt_machine_id])
            machines[virt_machine_id] = machine_attrs

        # store the updated constraints back in the metadata
        # the actual machine creation will happen later, during deploy
        # we have to reassign it to the bundle because the getter can
        # return a new empty dict without storing it back in the bundle
        juju_machines.update(machines)
        app.metadata_controller.bundle.machines = juju_machines

    async def deploy_one(self, application):
        """Ensures that the data in app.metadata_controller is
        up to date for the given application and mark it as "deployed".

        The actual deploy will happen after bootstrap in another controller.
        """
        if application not in self.undeployed_applications:
            app.log.error('Skipping attempt to deploy unavailable '
                          '{}'.format(application))
            return
        self.undeployed_applications.remove(application)

        await self.ensure_machines(application)
        self.apply_assignments(application)

        # We have to update the metadata_controller directly because the list
        # of applications we get from bundle.services is actually a view, so
        # updates to those don't persist back, combined with the fact that
        # bundleplacer doesn't provide any setters to store that data back
        bundle = app.metadata_controller.bundle
        sd = bundle._bundle[bundle.application_key][application.service_name]
        sd['num_units'] = application.num_units
        sd['options'] = application.options
        sd['to'] = application.placement_spec

    async def deploy_all(self):
        "deploys all un-deployed applications"
        for application in self.undeployed_applications:
            await self.deploy_one(application)
        self.finish()

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

    def finish(self):
        self.sync_assignment_opts()
        common.write_bundle(self.assignments)
        return controllers.use('bootstrap').render()

    def render(self, going_back=False):
        if going_back:
            # coming back from config or architecture view
            self.list_view.update_units()
            self.list_view.show()
            return

        self.applications = sorted(app.metadata_controller.bundle.services,
                                   key=attrgetter('service_name'))
        self.undeployed_applications = self.applications[:]

        if app.provider.cloud_type == cloud_types.MAAS:
            app.loop.create_task(self.connect_maas())

        self.list_view = ApplicationListView(self.applications,
                                             self.deploy_one,
                                             self.deploy_all,
                                             self.do_configure,
                                             self.do_architecture,
                                             self.back)
        self.list_view.show()

    def back(self):
        controllers.use('showsteps').render(going_back=True)


_controller_class = ConfigAppsController
