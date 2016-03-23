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

from collections import defaultdict
from concurrent.futures import Future
from functools import partial
import json
import requests
from threading import RLock

from bundleplacer.async import submit
from bundleplacer.relationtype import RelationType


class MetadataController:

    def __init__(self, placement_controller, config):
        self.placement_controller = placement_controller
        self.config = config
        self.charm_names = placement_controller.charm_names()
        # charm_name : charm_metadata full dict
        self.charm_info = {}
        # charm_name : requires/provides lists
        self.iface_info = {}
        self.metadata_future = None
        self.metadata_future_lock = RLock()
        self.charms_providing_iface = defaultdict(list)
        self.charms_requiring_iface = defaultdict(list)
        self.get_recommended_charm_names()
        self.load(self.charm_names + self.recommended_charm_names)

    def get_recommended_charm_names(self):
        if not self.config.getopt('config_filename'):
            self.recommended_charm_names = []
            return
        with open(self.config.getopt('config_filename')) as cf:
            bundle_config = json.load(cf)
        key = self.config.getopt('bundle_key')
        bundles = bundle_config['bundles']

        if type(bundles) == type([]):
            bundle_dict = next((d for d in bundles if d['key'] == key),
                               {})
        else:
            bundle_dict = bundles[key]
        self.recommended_charm_names = bundle_dict.get('recommendedCharms',
                                                       [])

    def load(self, charm_names):
        if self.metadata_future:
            # just wait for successive loads:
            self.metadata_future.result()

        with self.metadata_future_lock:
            self.metadata_future = submit(partial(self._do_load,
                                                  charm_names),
                                          self.handle_search_error)

    def _do_load(self, charm_names):
        ids = "&".join(["id={}".format(n) for n in charm_names])
        url = 'https://api.jujucharms.com/v4/meta/any?include=charm-metadata&'
        url += ids
        r = requests.get(url)
        metas = r.json()
        for charm_name, charm_dict in metas.items():
            md = charm_dict["Meta"]["charm-metadata"]
            self.charm_info[charm_name] = charm_dict
            rd = md.get("Requires", {})
            pd = md.get("Provides", {})
            requires = []
            provides = []
            for relname, d in rd.items():
                iface = d["Interface"]
                requires.append((relname, iface))
                self.charms_requiring_iface[iface].append((relname,
                                                           charm_name))

            for relname, d in pd.items():
                iface = d["Interface"]
                provides.append((relname, iface))
                self.charms_providing_iface[iface].append((relname,
                                                           charm_name))

            self.iface_info[charm_name] = dict(requires=requires,
                                               provides=provides)

    def loaded(self):
        return self.metadata_future.done()

    def add_charm(self, charm_name):
        if charm_name not in self.charm_info:
            self.load([charm_name])

    def get_provides(self, charm_name):
        if not self.loaded():
            return []
        return self.iface_info[charm_name]['provides']

    def get_requires(self, charm_name):
        if not self.loaded():
            return []
        return self.iface_info[charm_name]['requires']

    def get_charm_info(self, charm_name):
        if not self.loaded():
            return None
        return self.charm_info[charm_name]

    def get_services_for_iface(self, iface, reltype):
        services = []
        if reltype == RelationType.Requires:
            cs = self.charms_requiring_iface[iface]
        else:
            cs = self.charms_providing_iface[iface]

        for relname, charm_name in cs:
            pc = self.placement_controller
            services += [(relname, s) for s in
                         pc.services_with_charm(charm_name)]

        return services

    def handle_search_error(self, e):
        pass                    # TODO MMCC


class CharmStoreAPI:
    """Concurrently lookup data from the juju charm store.

    use the get_* functions to get a Future whose result will be the
    requested charm info

    """
    _cache = {}
    _cachelock = RLock()

    def __init__(self):
        self.baseurl = 'https://api.jujucharms.com/v4'

    def _do_remote_lookup(self, charm_name, metakey):
        url = (self.baseurl + '/meta/' +
               'any?include=charm-metadata&id={}'.format(charm_name))
        r = requests.get(url)
        rj = r.json()
        if len(rj.items()) != 1:
            raise Exception("Got wrong number of results from charm store")
        entity = list(rj.values())[0]
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

    def get_matches(self, substring, exc_cb):
        def _do_search():
            url = (self.baseurl +
                   "/search?text={}&autocomplete=1".format(substring) +
                   "&limit=5&include=charm-metadata&include=bundle-metadata")
            charm_url = url + "&type=charm"
            bundle_url = url + "&type=bundle"
            cr = requests.get(charm_url)
            crj = cr.json()
            br = requests.get(bundle_url)
            brj = br.json()
            return brj['Results'], crj['Results']

        f = submit(_do_search, exc_cb)
        return f
