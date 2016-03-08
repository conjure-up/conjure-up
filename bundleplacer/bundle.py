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

from concurrent.futures import Future
from functools import partial
import logging
from theblues.charmstore import CharmStore
from threading import RLock
import yaml
from bundleplacer.async import submit
from bundleplacer.service import Service
from bundleplacer.assignmenttype import AssignmentType, label_to_atype

log = logging.getLogger('bundleplacer')


class CharmStoreAPI:
    """Concurrently lookup data from the juju charm store.

    use the get_* functions to get a Future whose result will be the
    requested charm info

    """
    _charmstore = None
    _cache = {}
    _cachelock = RLock()

    def __init__(self):
        if not CharmStoreAPI._charmstore:
            csurl = 'https://api.jujucharms.com/v4'
            CharmStoreAPI._charmstore = CharmStore(csurl)

    def _do_remote_lookup(self, charm_name, metakey):
        entity = CharmStoreAPI._charmstore.entity(charm_name)
        with CharmStoreAPI._cachelock:
            CharmStoreAPI._cache[charm_name] = entity
        return entity

    def _wait_for_pending_lookup(self, f, charm_name, metakey):
        try:
            entity = f.result()
        except:
            return None

        if metakey is None:
            return entity
        return entity['Meta']['charm-metadata'][metakey]

    def _lookup(self, charm_name, metakey, exc_cb):
        with CharmStoreAPI._cachelock:
            if charm_name in CharmStoreAPI._cache:
                val = CharmStoreAPI._cache[charm_name]
                if isinstance(val, Future):
                    f = submit(partial(self._wait_for_pending_lookup,
                                       val, charm_name, metakey),
                               exc_cb)
                else:
                    if metakey is None:
                        d = val
                    else:
                        d = val['Meta']['charm-metadata'][metakey]
                    f = submit(lambda: d, exc_cb)
            else:
                whole_entity_f = submit(partial(self._do_remote_lookup,
                                                charm_name,
                                                metakey),
                                        exc_cb)
                CharmStoreAPI._cache[charm_name] = whole_entity_f

                f = submit(partial(self._wait_for_pending_lookup,
                                   whole_entity_f, charm_name,
                                   metakey),
                           exc_cb)

        return f

    def get_summary(self, charm_name, exc_cb):
        return self._lookup(charm_name, 'Summary', exc_cb)

    def get_entity(self, charm_name, exc_cb):
        return self._lookup(charm_name, None, exc_cb)


def create_service(servicename, service_dict, servicemeta, relations):
    # some attempts to guess at subordinate status from bundle format,
    # to avoid having to include it in metadata:

    # This doesn't work because bundles with no machines might
    # just use the juju default:

    # is_subordinate = 'to' not in service_dict.keys()

    is_subordinate = service_dict.get('num_units', 0) == 0

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
                      allow_multi_units=servicemeta.get('allow_multi_units', True),
                      subordinate=is_subordinate,
                      required=servicemeta.get('required', True),
                      relations=myrelations)

    # Make sure to map any strings to an assignment type enum
    if any(isinstance(atype, str)
           for atype in service.allowed_assignment_types):
        service.allowed_assignment_types = label_to_atype(
            service.allowed_assignment_types)
    return service


class Bundle:
    def __init__(self, filename, metadatafilename):
        self.filename = filename
        self.metadatafilename = metadatafilename
        with open(self.filename) as f:
            self._bundle = yaml.load(f)
        if metadatafilename:
            with open(self.metadatafilename) as f:
                self._metadata = yaml.load(f)
        else:
            self._metadata = {}
        if 'services' not in self._bundle.keys():
            raise Exception("Invalid Bundle.")

    def add_new_service(self, charm_name, charm_dict, service_name=None):
        if service_name is None:
            i = 1
            service_name = charm_name
            while service_name in self._bundle['services']:
                service_name = "{}-{}".format(charm_name, i)
                i += 1

        new_dict = {'charm': charm_dict['Id'],
                    'num_units': 1}
        self._bundle['services'][service_name] = new_dict

    def add_relation(self, s1_name, s1_rel, s2_name, s2_rel):
        r = ["{}:{}".format(s1_name, s1_rel),
             "{}:{}".format(s2_name, s2_rel)]
        self._bundle['relations'].append(r)

    def is_related(self, s1_name, s1_rel, s2_name, s2_rel):
        """Checks if a relation exists. If the relation in the bundle does not
        specify relation names, this returns true for any relation names.
        """
        a = "{}:{}".format(s1_name, s1_rel)
        b = "{}:{}".format(s2_name, s2_rel)
        rels = self._bundle['relations']
        return ([a, b] in rels or [b, a] in rels or
                [s1_name, s2_name] in rels or
                [s2_name, s1_name] in rels)
    
    @property
    def services(self):
        services = []
        metadata = self._metadata.get('services', {})
        bundle_services = self._bundle.get('services', {})
        relations = self._bundle.get('relations', [])
        for servicename, sd in bundle_services.items():
            sm = metadata.get(servicename, {})
            services.append(create_service(servicename, sd,
                                           sm, relations))
        return services

    def extra_items(self):
        return {k: v for k, v in self._bundle.items()
                if k not in ['services', 'machines', 'relations']}

