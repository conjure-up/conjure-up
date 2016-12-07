# Copyright 2016 Canonical, Ltd.
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

import logging
import os

import yaml

from bundleplacer.assignmenttype import AssignmentType, label_to_atype
from bundleplacer.charmstore_api import CharmStoreID
from bundleplacer.consts import DEFAULT_SERIES
from bundleplacer.service import Service

log = logging.getLogger('bundleplacer')


class keydict(dict):

    def __missing__(self, key):
        return key


class BundleFormatError(Exception):
    "Used to notify user about a bundle that can't be read."


def create_service(servicename, service_dict, servicemeta, relations):

    # a little cleaning to normalize a dict from the charmstore v4 api:
    service_dict = {k.lower(): v for k, v in service_dict.items()}
    if 'num_units' not in service_dict:
        service_dict['num_units'] = service_dict.get('numunits', 0)

    # some attempts to guess at subordinate status from bundle format,
    # to avoid having to include it in metadata:

    # This doesn't work because bundles with no machines might
    # just use the juju default:

    # is_subordinate = 'to' not in service_dict.keys()

    is_subordinate = service_dict.get('num_units', 0) == 0

    if 'charm' not in service_dict:
        m = "Service '{}' has no 'charm' key.".format(servicename)
        if 'branch' in service_dict:
            m += " 'branch' key is not supported."
        raise BundleFormatError(m)

    charm_name = service_dict['charm'].split('/')[-1]
    charm_name = '-'.join(charm_name.split('-')[:-1])

    myrelations = []
    for src, dst in relations:
        if src.startswith(servicename) or dst.startswith(servicename):
            myrelations.append((src, dst))

    service = Service(service_name=servicename,
                      charm_source=service_dict['charm'],
                      summary_future=None,
                      constraints=servicemeta.get('constraints', {}),
                      depends=servicemeta.get('depends', []),
                      conflicts=servicemeta.get('conflicts', []),
                      allowed_assignment_types=servicemeta.get(
                          'allowed_assignment_types',
                          list(AssignmentType)),
                      num_units=service_dict.get('num_units', 1),
                      options=service_dict.get('options', {}),
                      allow_multi_units=servicemeta.get('allow_multi_units',
                                                        True),
                      subordinate=is_subordinate,
                      required=servicemeta.get('required', True),
                      relations=myrelations,
                      placement_spec=service_dict.get('to', None),
                      expose=service_dict.get('expose', False))

    # Make sure to map any strings to an assignment type enum
    if any(isinstance(atype, str)
           for atype in service.allowed_assignment_types):
        service.allowed_assignment_types = label_to_atype(
            service.allowed_assignment_types)
    return service


class BundleMergeException(Exception):
    """Error merging two bundles"""


class Bundle:

    def __init__(self, filename=None, metadatafilename=None,
                 bundle_data=None, metadata=None):
        assert(filename or bundle_data)
        self.filename = filename
        self.metadatafilename = metadatafilename
        if self.filename:
            if os.path.exists(self.filename):
                with open(self.filename) as f:
                    self._bundle = yaml.load(f)
            else:
                self._bundle = dict(series=DEFAULT_SERIES,
                                    services={},
                                    machines={},
                                    relations=[])
        else:
            self._bundle = bundle_data
        if metadatafilename:
            with open(self.metadatafilename) as f:
                self._metadata = yaml.load(f)
        elif metadata:
            self._metadata = metadata
        else:
            self._metadata = {}

        self.application_key = 'services'
        if 'applications' in self._bundle.keys():
            self.application_key = 'applications'

        self._bundle = {k.lower(): v for
                        k, v in self._bundle.items()}
        for k in ['machines', self.application_key]:
            for name, val in self._bundle.get(k, {}).items():
                self._bundle[k][name] = {key.lower(): v for
                                         key, v in val.items()}

        if self.application_key not in self._bundle.keys():
            raise Exception("Invalid Bundle.")

    def add_new_service(self, charm_name, charm_dict, service_name=None,
                        is_subordinate=False):
        if service_name is None:
            i = 1
            service_name = charm_name
            while service_name in self._bundle[self.application_key]:
                service_name = "{}-{}".format(charm_name, i)
                i += 1

        new_dict = {'charm': charm_dict['Id'],
                    'num_units': 0 if is_subordinate else 1}
        self._bundle[self.application_key][service_name] = new_dict
        return service_name

    def remove_service(self, service_name):
        if service_name in self._bundle[self.application_key]:
            del self._bundle[self.application_key][service_name]

        for r1, r2 in self._bundle['relations']:
            s1 = r1.split(':')[0]
            s2 = r2.split(':')[0]
            if s1 == service_name or s2 == service_name:
                self._bundle['relations'].remove([r1, r2])

    def scale_service(self, service_name, amount):
        sd = self._bundle[self.application_key][service_name]
        new = sd.get('num_units', 0) + amount
        if new > 0:
            sd['num_units'] = new

    def add_relation(self, s1_name, s1_rel, s2_name, s2_rel):
        r = ["{}:{}".format(s1_name, s1_rel),
             "{}:{}".format(s2_name, s2_rel)]
        self._bundle['relations'].append(r)

    def remove_relation(self, s1_name, s1_rel, s2_name, s2_rel):
        r = self.find_relation(s1_name, s1_rel, s2_name, s2_rel)
        self._bundle['relations'].remove(r)

    def is_related(self, s1_name, s1_rel, s2_name, s2_rel):
        """Checks if a relation exists. If the relation in the bundle does not
        specify relation names, this returns true for any relation names.
        """
        r = self.find_relation(s1_name, s1_rel, s2_name, s2_rel)
        return r is not None

    def find_relation(self, s1_name, s1_rel, s2_name, s2_rel):
        a = "{}:{}".format(s1_name, s1_rel)
        b = "{}:{}".format(s2_name, s2_rel)
        rels = self._bundle['relations']
        for x in [[a, b], [b, a], [s1_name, s2_name], [s2_name, s1_name]]:
            if x in rels:
                return x
        return None

    def set_option(self, service_name, opname, value):
        sd = self._bundle[self.application_key][service_name]
        opts = sd.setdefault('options', {})
        opts[opname] = value

    @property
    def services(self):
        services = []
        metadata = self._metadata.get(self.application_key, {})
        bundle_services = self._bundle.get(self.application_key, {})
        relations = self._bundle.get('relations', [])
        for servicename, sd in bundle_services.items():
            sm = metadata.get(servicename, {})
            service = create_service(servicename, sd,
                                     sm, relations)
            if service.csid.series == "":
                service.csid.series = self.series
            services.append(service)
        return services

    @property
    def charm_ids(self):
        seen = set()
        return [s.charm_source for s in self.services
                if s.charm_source not in seen and not seen.add(s.charm_source)]

    def services_with_charm_id(self, charm_id):
        l = []
        csid = CharmStoreID(charm_id)
        id_no_rev = csid.as_str_without_rev()
        for service in self.services:
            if service.csid.as_str_without_rev() == id_no_rev:
                l.append(service)
        return l

    @property
    def machines(self):
        return self._bundle.get('machines', {})

    @machines.setter
    def machines(self, new_machines):
        self._bundle['machines'] = new_machines

    def add_machine(self, md, idx):
        if 'machines' not in self._bundle:
            self._bundle['machines'] = {}
        self._bundle['machines'][idx] = md

    @property
    def series(self):
        return self._bundle.get('series', DEFAULT_SERIES)

    def clear_machines_and_placement(self):
        self._bundle['machines'] = {}
        for sname, sd in self._bundle[self.application_key].items():
            if 'to' in sd:
                del(sd['to'])

    @property
    def assignments(self):
        """returns a dict of service_name: [to-strings]"""
        assert self.application_key in self._bundle
        assignments = {}
        for sname, sd in self._bundle[self.application_key].items():
            if 'to' in sd:
                assignments[sname] = sd['to']
        return assignments

    def extra_items(self):
        return {k: v for k, v in self._bundle.items()
                if k not in [self.application_key, 'machines', 'relations']}

    def update(self, other_bundle):
        """Merges one bundle with another, renaming any duplicate service
        names or machine names.

        returns a pair: (new_machines, new_services, new_assignments)
        """
        new_machines = {}
        new_service_names = []
        new_assignments = {}

        assert self.application_key in self._bundle

        # check for conflicts that can't be resolved by renaming
        for k, v in self._bundle.items():
            if k in [self.application_key, 'machines', 'relations']:
                continue
            if self._bundle[k] != other_bundle._bundle[k]:
                m = ("Can't merge top level key '{}': "
                     "{} vs {}".format(k, self._bundle[k],
                                       other_bundle._bundle[k]))
                raise BundleMergeException(m)

        service_renames = keydict()
        for sname, sd in other_bundle._bundle[self.application_key].items():
            newname = sname
            idx = 1
            while newname in self._bundle[self.application_key]:
                newname = sname + "-{}".format(idx)
                idx += 1
            service_renames[sname] = newname

        # generate machine renames and merge machines
        machine_renames = keydict()
        n_machines_mine = len(self._bundle.get('machines', {}))
        other_machines = other_bundle._bundle.get('machines', {})
        for mname, md in other_machines.items():
            if mname in self._bundle['machines']:
                newname = str(int(mname) + n_machines_mine)
                machine_renames[mname] = newname
            self._bundle['machines'][machine_renames[mname]] = md
            new_machines[machine_renames[mname]] = md

        # apply service renames to relations
        def rename_relation(r, rd):
            parts = r.split(":")
            if len(parts) > 1:
                return "{}:{}".format(rd[parts[0]],
                                      parts[1])
            else:
                return rd[parts[0]]

        for (or1, or2) in other_bundle._bundle.get('relations', []):
            nr1 = rename_relation(or1, service_renames)
            nr2 = rename_relation(or2, service_renames)
            if [nr1, nr2] in self._bundle['relations'] or\
               [nr2, nr1] in self._bundle['relations']:
                continue
            self._bundle['relations'].append([nr1, nr2])

        # apply machine renames to services
        def rename_machine(to, md):
            parts = to.split(":")
            if len(parts) > 1:
                return "{}:{}".format(parts[0],
                                      md[parts[1]])
            else:
                return md[parts[0]]

        for sname, sd in other_bundle._bundle[self.application_key].items():
            new_sd = sd.copy()
            if 'to' in sd:
                new_sd['to'] = [rename_machine(to, machine_renames)
                                for to in sd['to']]
            self._bundle[self.application_key][service_renames[sname]] = new_sd
            new_service_names.append(service_renames[sname])
            if 'to' in sd:
                new_assignments[service_renames[sname]] = new_sd['to']

        new_services = [s for s in self.services
                        if s.service_name in new_service_names]

        return new_machines, new_services, new_assignments
