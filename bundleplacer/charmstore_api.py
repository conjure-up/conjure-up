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

import json
from collections import defaultdict
from concurrent.futures import Future
from functools import partial
from threading import RLock

import requests

from bundleplacer.async import submit
from bundleplacer.consts import DEFAULT_SERIES
from bundleplacer.relationtype import RelationType


class CharmStoreID:

    def __init__(self, id_string, use_default_series=False):
        if id_string.startswith("cs:"):
            id_string = id_string[3:]
        cs = id_string.split('/')
        self.idtype = 'charm'
        self.series = ""
        self.owner = ""

        if len(cs) == 1:
            if use_default_series:
                self.series = DEFAULT_SERIES
            self.name, self.rev = self.parse_namerev(cs[0])

        elif len(cs) == 2:
            if cs[0].startswith("~"):
                if use_default_series:
                    self.series = DEFAULT_SERIES
                self.owner = cs[0][1:]
            else:
                self.series = cs[0]
            self.name, self.rev = self.parse_namerev(cs[1])

        elif len(cs) == 3:
            self.owner = cs[0]
            if self.owner.startswith("~"):
                self.owner = self.owner[1:]
            self.series = cs[1]
            self.name, self.rev = self.parse_namerev(cs[2])

        if self.series == 'bundle':
            self.idtype = 'bundle'

    def parse_namerev(self, nr):
        if '-' not in nr:
            return nr, ""
        name, rev = nr.rsplit('-', 1)
        if not rev.isdecimal():
            return nr, ""
        return name, rev

    def as_str_without_rev(self, include_scheme=True):
        s = "cs:" if include_scheme else ""
        if self.owner != "":
            s += "~" + self.owner + "/"
        if self.series != "":
            s += self.series + "/"
        s += self.name
        return s

    def as_str(self, include_scheme=True):
        s = self.as_str_without_rev(include_scheme)
        if self.rev != "":
            s += "-" + self.rev
        return s

    def as_seriesname(self):
        return "{}/{}".format(self.series, self.name)

    def __repr__(self):
        l = ["name: {}".format(self.name),
             "rev: {}".format(self.rev),
             "type: {}".format(self.idtype),
             "owner: {}".format(self.owner),
             "series: {}".format(self.series)]

        return "\n".join(l)


class MetadataController:

    def __init__(self, bundle, config, error_cb=None):
        self.bundle = bundle
        self.config = config
        self.error_cb = error_cb
        self.series = bundle.series
        self.charm_ids = bundle.charm_ids
        # charm_name : charm_metadata full dict
        self.charm_info = {}
        # charm_name : requires/provides lists
        self.iface_info = {}
        # charm_name : first paragraph of readme
        self.readmes = {}
        self.readme_futures = {}
        self.readme_callbacks = {}
        self.metadata_future = None
        self.metadata_future_lock = RLock()
        self.info_callbacks = []
        self.charms_providing_iface = defaultdict(list)
        self.charms_requiring_iface = defaultdict(list)
        self.get_recommended_charm_names()
        self.load(self.charm_ids + self.recommended_charm_names)

    def get_recommended_charm_names(self):
        if not self.config.getopt('config_filename'):
            self.recommended_charm_names = []
            return
        with open(self.config.getopt('config_filename')) as cf:
            bundle_config = json.load(cf)
        key = self.config.getopt('bundle_key')
        bundles = bundle_config['bundles']

        if isinstance(bundles, list):
            bundle_dict = next((d for d in bundles if d['key'] == key),
                               {})
        else:
            bundle_dict = bundles[key]
        self.recommended_charm_names = bundle_dict.get('recommendedCharms',
                                                       [])

    def load(self, charm_names_or_sources, done_cb=None):
        if len(charm_names_or_sources) == 0:
            return

        if self.metadata_future:
            # just wait for successive loads:
            self.metadata_future.result()

        with self.metadata_future_lock:
            self.metadata_future = submit(partial(self._do_load,
                                                  charm_names_or_sources),
                                          self.handle_search_error)
            if done_cb:
                self.metadata_future.add_done_callback(done_cb)
            self.metadata_future.add_done_callback(self.handle_load_done)

    def _request_readme(self, charm_id, short_charm_id):
        readme_url = ("https://api.jujucharms.com/charmstore"
                      "/v5/{}/readme".format(charm_id))
        r = requests.get(readme_url)
        if r.ok:
            t = r.text
        else:
            t = "No README available"
        self.readmes[short_charm_id] = t
        return t

    def request_readme(self, charm_id, short_charm_id):
        rf = submit(
            partial(self._request_readme, charm_id, short_charm_id),
            lambda _: None)
        self.readme_futures[short_charm_id] = rf

        cb = self.readme_callbacks.get(short_charm_id, None)
        if cb:
            rf.add_done_callback(cb)

    def _do_load(self, charm_names_or_sources):
        ids = []
        for n in charm_names_or_sources:
            csid = CharmStoreID(n)
            ids.append("id={}".format(csid.as_str_without_rev()))
        ids_str = "&".join(ids)
        url = 'https://api.jujucharms.com/charmstore/v5'
        url += '/meta/any?include=charm-metadata&'
        url += 'include=charm-config&'
        url += ids_str
        r = requests.get(url)
        if not r.ok:
            raise Exception("metadata loading failed: charms={} url={}".format(
                charm_names_or_sources, url))
        metas = r.json()

        for charm_name, charm_dict in sorted(metas.items()):
            md = charm_dict["Meta"]["charm-metadata"]
            csid = CharmStoreID(charm_name)
            id_no_rev = csid.as_str_without_rev()
            if id_no_rev in self.charm_info:
                continue

            self.charm_info[id_no_rev] = charm_dict

            if csid.series == "":
                csid.series = self.bundle.series
                id_no_rev_with_default_series = csid.as_str_without_rev()
                self.charm_info[id_no_rev_with_default_series] = charm_dict

            self.request_readme(csid.as_str(include_scheme=False),
                                csid.as_seriesname())

            rd = md.get("Requires", {})
            pd = md.get("Provides", {})
            requires = []
            provides = []
            for relname, d in rd.items():
                iface = d["Interface"]
                requires.append((relname, iface))
                self.charms_requiring_iface[iface].append((relname,
                                                           id_no_rev))

            for relname, d in pd.items():
                iface = d["Interface"]
                provides.append((relname, iface))
                self.charms_providing_iface[iface].append((relname,
                                                           id_no_rev))
            provides.append(('juju-info', 'juju-info'))
            self.charms_providing_iface['juju-info'].append(('juju-info',
                                                             id_no_rev))
            self.iface_info[id_no_rev] = dict(requires=requires,
                                              provides=provides)

    def get_recommended_charms(self):
        if not self.loaded():
            return []
        return [self.charm_info[CharmStoreID(n).as_str_without_rev()]
                for n in self.recommended_charm_names]

    def loaded(self):
        if self.metadata_future is None:
            return True
        return self.metadata_future.done()

    def handle_load_done(self, future):
        for charm_name, cb in self.info_callbacks:
            try:
                cb(self.charm_info[charm_name])
            except:
                pass

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

    def get_charm_info(self, charm_name, cb):
        if not self.loaded():
            self.info_callbacks.append((charm_name, cb))
            return None
        cb(self.charm_info[charm_name])
        return self.charm_info[charm_name]

    def get_readme(self, short_charm_id, cb):
        readme = self.readmes.get(short_charm_id, None)
        if readme:
            f = submit(lambda: readme, None)
            f.add_done_callback(cb)
            return

        readme_f = self.readme_futures.get(short_charm_id, None)
        if readme_f:
            readme_f.add_done_callback(cb)
        else:
            self.readme_callbacks[short_charm_id] = cb

    def get_services_for_iface(self, iface, reltype):
        services = []
        if reltype == RelationType.Requires:
            cs = self.charms_requiring_iface[iface]
        else:
            cs = self.charms_providing_iface[iface]
        for relname, charm_id in cs:
            services += [(relname, s) for s in
                         self.bundle.services_with_charm_id(charm_id)]

        return services

    def get_options(self, charm_name):
        if not self.loaded():
            return {}
        return self.charm_info[charm_name]['Meta']['charm-config']['Options']

    def get_resources(self, charm):
        resource_url = ("https://api.jujucharms.com/charmstore/v5/meta/any"
                        "?include=resources&id={}".format(charm))
        r = requests.get(resource_url)
        if r.ok:
            resources = r.json()
            resources = resources[charm]['Meta']['resources']
            for r in resources:
                r['Origin'] = 'store'
            return resources
        else:
            raise Exception("API error getting resource info for "
                            "charm={} url={}".format(charm, resource_url))

    def handle_search_error(self, e):
        self.error_cb(e)


class CharmStoreAPI:
    """Concurrently lookup data from the juju charm store.

    use the get_* functions to get a Future whose result will be the
    requested charm info

    """
    _cache = {}
    _cachelock = RLock()

    def __init__(self, series):
        self.baseurl = 'https://api.jujucharms.com/charmstore/v5'
        self.series = series

    def _do_remote_lookup(self, charm_name, metakey):
        url = (self.baseurl + '/meta/' +
               'any?include=charm-metadata&id={}/{}'.format(self.series,
                                                            charm_name))
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
                   "&limit=20&include=charm-metadata&include=bundle-metadata")
            charm_url = url + "&type=charm&series={}".format(self.series)
            bundle_url = url + "&type=bundle"
            cr = requests.get(charm_url)
            crj = cr.json()
            br = requests.get(bundle_url)
            brj = br.json()
            return brj['Results'], crj['Results']

        f = submit(_do_search, exc_cb)
        return f
