import yaml

from bundleplacer.assignmenttype import AssignmentType


class BundleWriter:

    def __init__(self, assignments, bundle):
        # assignments is a dict mapping juju machine ID to a list of
        # (application, application type) pairs.
        self.assignments = assignments
        self.bundle = bundle

    def _dict_for_service(self, svc, atype, to, serialized_services):

        tolist = []
        num_units = 1
        if svc.service_name in serialized_services:
            num_units = serialized_services[svc.service_name]['num_units'] + 1
            tolist = serialized_services[svc.service_name].get('to', [])

        d = dict(charm=svc.charm_source)
        if len(svc.options) > 0:
            d['options'] = svc.options
        if not svc.subordinate:
            d['num_units'] = num_units

        if to is not None:
            prefix = {AssignmentType.DEFAULT: "",
                      AssignmentType.BareMetal: "",
                      AssignmentType.KVM: "kvm:",
                      AssignmentType.LXD: "lxd:",
                      AssignmentType.LXC: "lxc:"}[atype]
            tolist.append("{}{}".format(prefix, to))

        if len(tolist) > 0:
            d['to'] = tolist
        return d

    def _dict_for_machine(self, mid):
        if '/' not in mid:
            return {}
        machine_tag = mid.split('/')[-2]
        cstr = "tags={}".format(machine_tag)
        return {"constraints": cstr}

    def _get_used_relations(self, services):
        relations = []
        service_names = [s.service_name for s in services]
        for svc in services:
            for src, dst in svc.relations:
                src_service = src.split(":")[0]
                dst_service = dst.split(":")[0]
                if src_service in service_names and \
                   dst_service in service_names:
                    relations.append([src, dst])
        # uniquify list of relations
        seen = set()
        return [r for r in relations
                if str(r) not in seen and not seen.add(str(r))]

    def write_bundle(self, filename):
        bundle = {}
        serialized_services = {}
        services = []
        machines = self.bundle.machines
        iid_map = {}            # maps iid to juju machine number

        # get a machine dict for every machine with at least one
        # service
        existing_ids = list(machines.keys()) + ["_subordinates", "_default"]
        for mid in machines.keys():
            iid_map[mid] = mid

        # assignments was {id: {atype: [service]}}
        # assignments is {id: [(service, atype)]}

        for iid, al in self.assignments.items():
            if len(al) == 0:
                continue

            if iid not in existing_ids:
                machine_id = "{}".format(len(machines) + 1)
                iid_map[iid] = machine_id
                machines[machine_id] = self._dict_for_machine(iid)

        mkeys = list(machines.keys())
        for machine_id in mkeys:
            q.q(self.assignments[machine_id])
            if len(self.assignments[machine_id]) < 1:
                del machines[machine_id]

        for iid, al in self.assignments.items():
            for svc, atype in al:
                sd = self._dict_for_service(svc, atype,
                                            iid_map.get(iid, None),
                                            serialized_services)
                serialized_services[svc.service_name] = sd
                services.append(svc)

        bundle['machines'] = machines
        bundle['services'] = serialized_services
        bundle['relations'] = self._get_used_relations(services)

        for k, v in self.bundle.extra_items().items():
            bundle[k] = v

        with open(filename, 'w') as f:
            yaml.dump(bundle, f, default_flow_style=False)
