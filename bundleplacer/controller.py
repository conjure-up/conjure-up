# Copyright 2014-2016 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict, Counter
import copy
import logging
import yaml
from multiprocessing import cpu_count

from bundleplacer.maas import (satisfies, MaasMachineStatus)
from bundleplacer.state import CharmState

from bundleplacer.assignmenttype import AssignmentType
from bundleplacer.bundle import Bundle

log = logging.getLogger('bundleplacer')


DEFAULT_SHARED_ASSIGNMENT_TYPE = AssignmentType.LXC


class PlaceholderMachine:

    """A dummy MaasMachine that doesn't map to an actual machine in MAAS.

    To specify a future virtual machine for placement that will be
    created later, pass in vm specs as juju constraints in 'constraints'.

    The keys juju uses differ somewhat from the MAAS API status keys,
    and are mapped so that they will appear correct to placement code
    expecting MAAS machines.
    """

    def __init__(self, instance_id, name, constraints=None):
        self.instance_id = instance_id
        self.system_id = instance_id
        self.machine_id = -1
        self.display_name = name
        def_cons = {'arch': '?',
                    'cpu_count': 0,
                    'cpu_cores': 0,
                    'memory': 0,
                    'mem': 0,
                    'storage': 0}
        if constraints is None:
            self.constraints = def_cons
        else:
            self.constraints = constraints

    @property
    def arch(self):
        return self.constraints['arch']

    @property
    def cpu_cores(self):
        return self.constraints['cpu_cores']

    def filter_label(self):
        return self.display_name

    @property
    def machine(self):
        return self.constraints

    @property
    def mem(self):
        return self.constraints['mem']

    @property
    def status(self):
        return MaasMachineStatus.UNKNOWN

    @property
    def storage(self):
        return self.constraints['storage']

    @property
    def hostname(self):
        return self.display_name

    def __repr__(self):
        return "<Placeholder Machine: {}>".format(self.display_name)


class PlacementError(Exception):

    "Generic exception class for placement related errors"


class PlacementController:

    """Keeps state of current machines and their assigned services.

    Maintains two placeholder machines, one for subordinate charms and
    one for "Juju Default" that are both the equivalent of not
    specifying a machine to deploy to when invoking Juju.

    """

    def __init__(self, maas_state=None, config=None):
        self.config = config
        self.maas_state = maas_state
        self._machines = []
        self.sub_placeholder = PlaceholderMachine('_subordinates',
                                                  'Subordinate Charms')
        self.def_placeholder = PlaceholderMachine('_default',
                                                  'Juju Default')
        # assignments is {id: {atype: [charm class]}}
        self.assignments = defaultdict(lambda: defaultdict(list))
        self.deployments = defaultdict(lambda: defaultdict(list))
        self.autosave_filename = None
        self.bundle = Bundle(config.getopt('bundle_filename'),
                             config.getopt('metadata_filename'))
        self.reset_assigned_deployed()

    def get_temp_copy(self):
        """Returns another PlacementController that can be used to track
        assignments temporarily, e.g. for supporting cancellable
        assignments in a dialog box.

        Pairs with update_from_controller() to 'commit' those temporary
        assignments to the 'main' controller.
        """
        newpc = PlacementController(maas_state=self.maas_state,
                                    config=self.config)
        newpc.assignments = copy.copy(self.assignments)
        newpc.deployments = copy.copy(self.deployments)
        newpc._machines = self._machines
        newpc.reset_assigned_deployed()
        return newpc

    def update_from_controller(self, other):
        """Updates internal structures based on other's.
        For integrating temporarily tracked updates."""

        self.assignments = other.assignments
        self.deployments = other.deployments
        self.reset_assigned_deployed()

    def set_assignments_from_deployments(self):
        """Reset deployment state of all services. Useful after reading a file
        from a previous install.
        """
        self.assignments = self.deployments
        self.deployments = defaultdict(lambda: defaultdict(list))
        self.reset_assigned_deployed()

    def __repr__(self):
        return "<PlacementController {}>".format(id(self))

    def set_autosave_filename(self, filename):
        self.autosave_filename = filename

    def do_autosave(self):
        if not self.autosave_filename:
            return
        with open(self.autosave_filename, 'w') as af:
            self.save(af)

    def save(self, f):
        """f is a file-like object to save state to, to be re-read by
        load(). No guarantees made about the contents of the file.
        """
        flat_assignments = defaultdict(dict)
        for iid, ad in self.assignments.items():

            flat_ad = {}
            for atype, al in ad.items():
                flat_al = [cc.charm_name for cc in al]
                flat_ad[atype.name] = flat_al

            flat_assignments[iid]['assignments'] = flat_ad

        for iid, dd in self.deployments.items():
            flat_dd = {}
            for atype, dl in dd.items():
                flat_dl = [cc.charm_name for cc in dl]
                flat_dd[atype.name] = flat_dl
            flat_assignments[iid]['deployments'] = flat_dd

        for iid in flat_assignments.keys():
            constraints = {}
            if self.maas_state is None:
                machine = next((m for m in self.machines() if
                                m.instance_id == iid), None)
                if machine:
                    constraints = machine.constraints
                    flat_assignments[iid]['constraints'] = constraints

        yaml.dump(flat_assignments, f)

    def load(self, f):
        """Load assignments from file object written to by save().
        replaces current assignments.
        """
        def find_charm_class(name):
            for cc in self.charm_classes():
                if cc.charm_name == name:
                    return cc
            log.warning("Could not find charm class "
                        "matching saved charm name {}".format(name))
            return None

        file_assignments = yaml.load(f)
        new_assignments = defaultdict(lambda: defaultdict(list))
        new_deployments = defaultdict(lambda: defaultdict(list))
        for iid, d in file_assignments.items():
            if self.maas_state is None and \
               not self.is_placeholder(iid):
                constraints = d.get('constraints', {})
                pm = PlaceholderMachine(iid, iid,
                                        constraints)
                self._machines.append(pm)

            ad = d.get('assignments', {})
            for atypestr, al in ad.items():
                new_al = [find_charm_class(ccname)
                          for ccname in al]
                new_al = [x for x in new_al if x is not None]
                at = AssignmentType.__members__[atypestr]
                new_assignments[iid][at] = new_al

            dd = d.get('deployments', {})
            for atypestr, dl in dd.items():
                new_dl = [find_charm_class(ccname)
                          for ccname in dl]
                new_dl = [x for x in new_dl if x is not None]
                at = AssignmentType.__members__[atypestr]
                new_deployments[iid][at] = new_dl

        self.assignments.clear()
        self.assignments.update(new_assignments)
        self.deployments.clear()
        self.deployments.update(new_deployments)
        self.reset_assigned_deployed()

    def update_and_save(self):
        self.reset_assigned_deployed()
        self.do_autosave()

    def is_placeholder(self, mid):
        return mid in [self.sub_placeholder.instance_id,
                       self.def_placeholder.instance_id]

    def machines(self, include_placeholders=True):
        """Returns all machines known to the controller.

        if 'include_placeholder' is False, any placeholder machines
        are excluded.
        """
        if self.maas_state:
            cons = self.config.getopt('constraints')
            ms = self.maas_state.machines(constraints=cons)
        else:
            ms = self._machines

        if include_placeholders:
            return ms + [self.sub_placeholder, self.def_placeholder]
        else:
            return ms

    def machines_pending(self, include_placeholders=False):
        """Returns a list of machines that have charms assigned to them which
        are not yet deployed.

        Excludes placeholder machines by default, so this can be used
        to e.g. get the number of real machines to wait for.

        """
        ms = []
        for m in self.machines(include_placeholders=include_placeholders):
            if m.instance_id in self.assignments:
                n = sum(len(cl) for _, cl in
                        self.assignments[m.instance_id].items())
                if n > 0:
                    ms.append(m)
        return ms

    def charm_classes(self):
        return self.bundle.charm_classes

    def assigned_charm_classes(self):
        """Returns a deduplicated list of all charms that have a placement
        assigned, but are not yet deployed.

        """
        return list(self.assigned_services)

    def deployed_charm_classes(self):
        """Returns a deduplicated list of all charms that have been deployed.
        """
        return list(self.deployed_services)

    def assign(self, machine, charm_class, atype):
        if not charm_class.allow_multi_units:
            for m, d in self.assignments.items():
                for at, l in d.items():
                    if charm_class in l:
                        l.remove(charm_class)

        self.assignments[machine.instance_id][atype].append(charm_class)
        self.update_and_save()

    def mark_deployed(self, machine, charm_class, atype):
        self.deployments[machine.instance_id][atype].append(charm_class)
        self.assignments[machine.instance_id][atype].remove(charm_class)
        self.update_and_save()

    def _get_machines_by_atype(self, a_dict, charm_class):
        "Helper for get_assignments and get_deployments"
        all_machines = self.machines()

        machines_by_atype = defaultdict(list)
        for m_id, d in a_dict.items():
            m = next((m for m in all_machines
                      if m.instance_id == m_id), None)
            if not m:
                log.debug("can't find machine for m_id '{}'".format(m_id))
                continue

            for atype, assignment_list in d.items():
                for c in assignment_list:
                    if c == charm_class:
                        machines_by_atype[atype].append(m)

        return machines_by_atype

    def get_assignments(self, charm_class):
        """returns assignments for a given charm

        returns a dict like {assignment_type : [machines]}
        """
        return self._get_machines_by_atype(self.assignments,
                                           charm_class)

    def get_deployments(self, charm_class):
        """returns deployments for a given charm

        returns a dict like {assignment_type : [machines]}
        """
        return self._get_machines_by_atype(self.deployments,
                                           charm_class)

    def clear_all_assignments(self):
        self.assignments = defaultdict(lambda: defaultdict(list))
        self.update_and_save()

    def clear_assignments(self, m):
        """clears all assignments for machine m.
        If m has no assignments, does nothing.
        """
        if m.instance_id not in self.assignments:
            return

        del self.assignments[m.instance_id]
        self.update_and_save()

    def remove_one_assignment(self, m, cc):
        ad = self.assignments[m.instance_id]
        for atype, assignment_list in ad.items():
            if cc in assignment_list:
                assignment_list.remove(cc)
                break
        self.update_and_save()

    def assignments_for_machine(self, m):
        """Returns all assignments for given machine

        {assignment_type: [charm_class]}
        """
        return self.assignments[m.instance_id]

    def deployments_for_machine(self, m):
        """Returns deployments
        {atype: [charm_class]}
        """
        return self.deployments[m.instance_id]

    def is_assigned_to(self, charm_class, machine):
        assignment_dict = self.assignments[machine.instance_id]
        for atype, charm_classes in assignment_dict.items():
            if charm_class in charm_classes:
                return True
        return False

    def is_deployed_to(self, charm_class, machine):
        dd = self.deployments[machine.instance_id]
        for atype, charm_classes in dd.items():
            if charm_class in charm_classes:
                return True
        return False

    def set_all_assignments(self, assignments):
        self.assignments = assignments
        self.update_and_save()

    def reset_assigned_deployed(self):
        self.assigned_services = set()
        self.deployed_services = set()
        for cc in self.charm_classes():
            ad = self.get_assignments(cc)
            is_assigned = False
            for atype, al in ad.items():
                if len(al) > 0:
                    is_assigned = True
            if is_assigned:
                self.assigned_services.add(cc)

            dd = self.get_deployments(cc)
            is_deployed = False
            for atype, dl in dd.items():
                if len(dl) > 0:
                    is_deployed = True
            if is_deployed:
                self.deployed_services.add(cc)

    def is_assigned(self, charm):
        return charm in self.assigned_services

    def is_deployed(self, charm):
        return charm in self.deployed_services

    def get_charm_state(self, charm):
        """Returns tuple of charm state:
        (state, cons, deps)

        state is a CharmState:

        - REQUIRED means that the charm still must be assigned before
        deploying is OK.

        IF a charm dependency forced this, then the other charm will
        be in 'deps'.  'deps' is NOT just a list of all charms that
        depend on the given charm.

        - CONFLICTED means that it can't be assigned until a conflicting
        charm is unassigned.  In this case, the conflicting charm is in
        'cons'.

        - OPTIONAL means that it is ok either way. deps and cons are unused

        """
        state = CharmState.OPTIONAL
        conflicting = set()
        depending = set()

        def conflicts_with(other_charm):
            return (charm.charm_name in other_charm.conflicts or
                    other_charm.charm_name in charm.conflicts)

        def depends(a_charm, b_charm):
            return b_charm.charm_name in a_charm.depends

        required_charms = [c for c in self.charm_classes()
                           if c.is_core]

        planned_or_deployed = (self.assigned_charm_classes() +
                               required_charms +
                               self.deployed_charm_classes())

        for other_charm in planned_or_deployed:
            if conflicts_with(other_charm):
                state = CharmState.CONFLICTED
                conflicting.add(other_charm)
            if depends(other_charm, charm):
                if state != CharmState.CONFLICTED:
                    state = CharmState.REQUIRED
                depending.add(other_charm)

        if charm.charm_name in [c.charm_name for c in required_charms]:
            state = CharmState.REQUIRED

        n_required = charm.required_num_units()
        # sanity check:
        if n_required > 1 and not charm.allow_multi_units:
            log.error("Inconsistent charm definition for {}:"
                      " - requires {} units but does not allow "
                      "multi units.".format(charm.charm_name, n_required))

        n_units = (self.assignment_machine_count_for_charm(charm) +
                   self.deployment_machine_count_for_charm(charm))

        if state == CharmState.OPTIONAL and \
           n_units > 0 and n_units < n_required:
            state = CharmState.REQUIRED
        elif state == CharmState.REQUIRED and n_units >= n_required:
            if n_units > 0:
                state = CharmState.OPTIONAL

        return (state, list(conflicting), list(depending))

    def unassigned_undeployed_services(self):
        all_charms = set(self.charm_classes())
        return (all_charms -
                (self.assigned_services.union(self.deployed_services)))

    def can_deploy(self):
        unassigned_requireds = [cc for cc in
                                self.unassigned_undeployed_services()
                                if self.get_charm_state(cc)[0] ==
                                CharmState.REQUIRED]

        underassigned = [cc for cc in self.assigned_services if
                         (self.assignment_machine_count_for_charm(cc) +
                          self.deployment_machine_count_for_charm(cc)) <
                         cc.required_num_units()]
        return len(unassigned_requireds) + len(underassigned) == 0

    def assignment_machine_count_for_charm(self, cc):
        """Returns the total number of assignments of any type for a given
        charm."""
        return sum([len(al) for al in self.get_assignments(cc).values()])

    def deployment_machine_count_for_charm(self, cc):
        """Returns the total number of deployments of any type for a given
        charm."""
        return sum([len(al) for al in self.get_deployments(cc).values()])

    def autoassign_unassigned_services(self):
        """Attempt to find machines for all required unassigned services using
        only empty machines.

        Returns a pair (success, message) where success is True if all
        services are assigned. message is an info message for the user.

        """

        empty_machines = [m for m in self.machines(include_placeholders=False)
                          if len(self.assignments[m.instance_id]) == 0]

        unassigned_services = list(self.unassigned_undeployed_services())
        unassigned_defaults = self.gen_defaults(unassigned_services,
                                                empty_machines)

        for mid, charm_classes in unassigned_defaults.items():
            self.assignments[mid] = charm_classes

        self.update_and_save()

        unassigned_services = list(self.unassigned_undeployed_services())
        unassigned_reqs = [c for c in unassigned_services if
                           self.get_charm_state(c)[0] == CharmState.REQUIRED]

        if len(unassigned_reqs) > 0:
            msg = ("Not enough empty machines could be found for the "
                   "following required services. Please add machines and "
                   "try again, or finish placement manually.")
            m = ", ".join([c.charm_name for c in unassigned_reqs])
            return (False, msg + "\n" + m)
        return (True, "")

    def autoassign_unassigned_to_default(self):
        """Assigns all unassigned services to juju default placeholder."""

        for s in self.unassigned_undeployed_services():
            d = self.assignments[self.def_placeholder.instance_id]
            al = d[DEFAULT_SHARED_ASSIGNMENT_TYPE]
            al.append(s)
        self.update_and_save()

    def gen_defaults(self, charm_classes=None, maas_machines=None):
        """Generates an assignments dictionary for the given charm classes and
        machines, based on constraints.

        Does not alter controller state.

        Use set_all_assignments(gen_defaults()) to clear and reset the
        controller's state to these defaults.

        Should not be used for single installs, see gen_single.
        """
        if self.maas_state is None:
            raise PlacementError("Can't call gen_defaults with no maas_state")

        if charm_classes is None:
            charm_classes = self.charm_classes()
        log.debug("in gen_defaults, charm_classes is {}".format(charm_classes))
        assignments = defaultdict(lambda: defaultdict(list))

        if maas_machines is None:
            maas_machines = self.maas_state.machines(
                MaasMachineStatus.READY,
                constraints=self.config.getopt('constraints'))

        def satisfying_machine(constraints):
            for machine in maas_machines:
                if satisfies(machine, constraints)[0]:
                    maas_machines.remove(machine)
                    return machine

            return None

        isolated_charms, controller_charms = [], []
        subordinate_charms = []

        for charm_class in charm_classes:
            state, _, _ = self.get_charm_state(charm_class)
            if state != CharmState.REQUIRED:
                continue
            if charm_class.isolate:
                assert(not charm_class.subordinate)
                isolated_charms.append(charm_class)
            elif charm_class.subordinate:
                assert(not charm_class.isolate)
                subordinate_charms.append(charm_class)
            else:
                controller_charms.append(charm_class)

        for charm_class in isolated_charms:
            for n in range(charm_class.required_num_units()):
                m = satisfying_machine(charm_class.constraints)
                if m:
                    l = assignments[m.instance_id][AssignmentType.BareMetal]
                    l.append(charm_class)

        controller_machine = satisfying_machine({})
        if controller_machine:
            for charm_class in controller_charms:
                ad = assignments[controller_machine.instance_id]
                l = ad[DEFAULT_SHARED_ASSIGNMENT_TYPE]
                l.append(charm_class)

        for charm_class in subordinate_charms:
            ad = assignments[self.sub_placeholder.instance_id]
            l = ad[AssignmentType.DEFAULT]
            l.append(charm_class)

        import pprint
        log.debug(pprint.pformat(assignments))
        return assignments

    def gen_single(self):
        """Generates an assignment for the single installer."""
        assignments = defaultdict(lambda: defaultdict(list))

        max_cpus = cpu_count()
        if max_cpus >= 2:
            max_cpus = min(8, max_cpus // 2)

        controller = PlaceholderMachine('controller', 'controller',
                                        {'mem': 6144,
                                         'root-disk': 20480,
                                         'cpu-cores': max_cpus})
        self._machines.append(controller)

        charm_name_counter = Counter()

        def placeholder_for_charm(charm_class):
            mnum = charm_name_counter[charm_class.charm_name]
            charm_name_counter[charm_class.charm_name] += 1

            instance_id = '{}-machine-{}'.format(charm_class.charm_name,
                                                 mnum)
            m_name = 'machine {} for {}'.format(mnum,
                                                charm_class.display_name)

            return PlaceholderMachine(instance_id, m_name,
                                      charm_class.constraints)

        for charm_class in self.charm_classes():
            state, _, _ = self.get_charm_state(charm_class)
            if state != CharmState.REQUIRED:
                continue
            if charm_class.isolate:
                assert(not charm_class.subordinate)
                for n in range(charm_class.required_num_units()):
                    pm = placeholder_for_charm(charm_class)
                    self._machines.append(pm)
                    ad = assignments[pm.instance_id]
                    ad[AssignmentType.DEFAULT].append(charm_class)
            elif charm_class.subordinate:
                assert(not charm_class.isolate)
                ad = assignments[self.sub_placeholder.instance_id]
                l = ad[AssignmentType.DEFAULT]
                l.append(charm_class)
            else:
                ad = assignments[controller.instance_id]
                ad[AssignmentType.LXC].append(charm_class)

        import pprint
        log.debug("gen_single() = '{}'".format(pprint.pformat(assignments)))
        return assignments


class BundleWriter:
    def __init__(self, controller):
        self.controller = controller

    def _dict_for_service(self, svc, atype, to, services):

        tolist = []
        num_units = 1
        if svc.charm_name in services:
            num_units = services[svc.charm_name]['num_units'] + 1
            tolist = services[svc.charm_name]['to']

        d = dict(charm=svc.charm_source,
                 num_units=num_units,
                 options=svc.options)
        if to is not None:
            prefix = {AssignmentType.DEFAULT: "",
                      AssignmentType.BareMetal: "",
                      AssignmentType.KVM: "kvm:",
                      AssignmentType.LXC: "lxc:"}[atype]
            tolist.append("{}{}".format(prefix, to))

        if len(tolist) > 0:
            d['to'] = tolist
        return d

    def _dict_for_machine(self, mid):
        machine_tag = mid.split('/')[-2]
        cstr = "tags={}".format(machine_tag)
        return {"constraints": cstr}

    def _get_used_relations(self, services):
        relations = []
        service_names = [s.charm_name for s in services]
        for svc in services:
            for src, dst in svc.relations:
                src_charm = src.split(":")[0]
                dst_charm = dst.split(":")[0]
                if src_charm in service_names and dst_charm in service_names:
                    relations.append([src, dst])
        # uniquify list of relations
        seen = set()
        return [r for r in relations
                if str(r) not in seen and not seen.add(str(r))]

    def write_bundle(self, filename):
        bundle = {}
        services = {}
        servicenames = []
        machines = {}
        iid_map = {}            # maps iid to juju machine number

        self.controller.autoassign_unassigned_to_default()

        # get a machine dict for every machine with at least one
        # service
        for iid, d in self.controller.assignments.items():
            if sum([len(svcs) for svcs in d.values()]) == 0:
                continue
            if iid not in ["_subordinates", "_default"]:
                machine_id = len(machines) + 1
                iid_map[iid] = machine_id
                machines[machine_id] = self._dict_for_machine(iid)

        for iid, d in self.controller.assignments.items():
            for atype, svcs in d.items():
                if len(svcs) < 1:
                    continue
                for svc in svcs:
                    sd = self._dict_for_service(svc, atype,
                                                iid_map.get(iid, None),
                                                services)
                    services[svc.charm_name] = sd
                    servicenames.append(svc)

        bundle['machines'] = machines
        bundle['services'] = services
        bundle['relations'] = self._get_used_relations(servicenames)

        for k, v in self.controller.bundle.extra_items().items():
            bundle[k] = v

        with open(filename, 'w') as f:
            yaml.dump(bundle, f, default_flow_style=False)
