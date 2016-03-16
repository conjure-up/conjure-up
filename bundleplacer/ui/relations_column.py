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
from enum import Enum
from functools import partial
import requests
from threading import RLock

from urwid import AttrMap, Divider, Pile, Text, WidgetWrap

from bundleplacer.async import submit

from ubuntui.widgets.buttons import MenuSelectButton

import logging

log = logging.getLogger('bundleplacer')


class RelationType(Enum):
    Requires = 0
    Provides = 1


class RelationWidget(WidgetWrap):

    def __init__(self, source_service_name, source_relname, interface,
                 reltype, target_service_name, target_relname,
                 placement_controller, select_cb):
        self.source_service_name = source_service_name
        self.source_relname = source_relname
        self.interface = interface
        self.reltype = reltype
        self.target_service_name = target_service_name
        self.target_relname = target_relname
        self.select_cb = select_cb
        self.placement_controller = placement_controller
        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def build_widgets(self):

        self.button = MenuSelectButton("",
                                       on_press=self.do_select)
        return AttrMap(self.button, 'text',
                       'button_secondary focus')

    def update(self):
        arrow = {RelationType.Provides: "\N{RIGHTWARDS ARROW}",
                 RelationType.Requires:
                 "\N{LEFTWARDS ARROW}"}[self.reltype]

        pc = self.placement_controller
        self.connected = pc.is_related(self.source_service_name,
                                       self.source_relname,
                                       self.target_service_name,
                                       self.target_relname)

        connstr = {True: "\N{CHECK MARK} ",
                   False: "  "}[self.connected]
            
        title = "{} {} {}  {}:{}".format(connstr,
                                         self.source_relname,
                                         arrow,
                                         self.target_service_name,
                                         self.target_relname)
        self.button.set_label(title)

    def do_select(self, sender):
        self.select_cb(self.source_relname, self.target_service_name,
                       self.target_relname)


class NoRelationWidget(WidgetWrap):
    def __init__(self, relname, iface, reltype):
        other_reltype = {RelationType.Requires: RelationType.Provides,
                         RelationType.Provides: RelationType.Requires}[reltype]
        self.source_relname = relname
        self.reltype = reltype
        s = "({}: nothing {} {})".format(
            relname, other_reltype.name.lower(), iface)
        super().__init__(AttrMap(MenuSelectButton(s), 'label',
                                 'button_secondary focus'))

    def selectable(self):
        return True

    def update(self):
        "no op"


class MetadataController:

    def __init__(self, placement_controller):
        self.placement_controller = placement_controller
        self.charm_names = placement_controller.charm_names()
        # charm_name : charm_metadata        
        self.charm_info = {}
        self.metadata_future = None
        self.metadata_future_lock = RLock()
        self.charms_providing_iface = defaultdict(list)
        self.charms_requiring_iface = defaultdict(list)
        
        self.load(self.charm_names)

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

            self.charm_info[charm_name] = dict(requires=requires,
                                               provides=provides)

    def loaded(self):
        return self.metadata_future.done()

    def add_charm(self, charm_name):
        if charm_name not in self.charm_info:
            self.load([charm_name])
    
    def get_provides(self, charm_name):
        if not self.loaded():
            return []
        return self.charm_info[charm_name]['provides']

    def get_requires(self, charm_name):
        if not self.loaded():
            return []
        return self.charm_info[charm_name]['requires']

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


class RelationsColumn(WidgetWrap):

    """UI to edit relations of a service
    """

    def __init__(self, display_controller, placement_controller,
                 placement_view):
        self.placement_controller = placement_controller
        self.metadata_controller = MetadataController(placement_controller)
        self.service = None
        self.provides = set()
        self.requires = set()
        self.placement_view = placement_view
        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def build_widgets(self):
        self.title = Text('')
        self.relation_widgets = []
        self.pile = Pile([Divider(), self.title] + self.relation_widgets)
        return self.pile

    def refresh(self):
        self.set_service(self.service)

    def add_charm(self, charm_name):
        self.metadata_controller.add_charm(charm_name)

    def set_service(self, service):
        self.service = service
        self.add_charm(service.charm_name)
        self.pile.contents = self.pile.contents[:2]
        self.provides = set()
        self.requires = set()
        self.relation_widgets = []

    def update(self):
        if self.service is None:
            return

        self.title.set_text(('body', "Edit relations for {}".format(
            self.service.service_name)))

        if len(self.relation_widgets) == 0:
            self.title.set_text(('body', "Loading Relations..."))
        else:
            self.title.set_text(('body', "Select Relations:"))

        p = set(self.metadata_controller.get_provides(self.service.charm_name))
        r = set(self.metadata_controller.get_requires(self.service.charm_name))
        new_provides = p - self.provides
        self.provides.update(p)
        new_requires = r - self.requires
        self.requires.update(r)

        mc = self.metadata_controller
        args = [(relname, iface, RelationType.Provides,
                 mc.get_services_for_iface(iface, RelationType.Requires))
                for relname, iface in sorted(new_provides)]
        
        args += [(relname, iface, RelationType.Requires,
                  mc.get_services_for_iface(iface, RelationType.Provides))
                 for relname, iface in sorted(new_requires)]

        for relname, iface, reltype, matches in args:
            if len(matches) == 0:
                rw = NoRelationWidget(relname, iface, reltype)
                self.relation_widgets.append(rw)
                self.pile.contents.append((rw,
                                           self.pile.options()))

            for tgt_relname, tgt_service in matches:
                if tgt_service.service_name == self.service.service_name:
                    continue
                rw = RelationWidget(self.service.service_name, relname,
                                    iface, reltype, tgt_service.service_name,
                                    tgt_relname,
                                    self.placement_controller,
                                    self.do_select)
                self.relation_widgets.append(rw)
                self.pile.contents.append((rw,
                                           self.pile.options()))

        for w, _ in self.pile.contents[2:]:
            w.update()
        self.sort_relation_widgets()

    def focus_prev_or_top(self):
        # ? self.pile.focus_position = len(self.pile.contents) - 1

        if len(self.pile.contents) <= 2:
            return
        pos = self.pile.focus_position
        if pos < 2:
            self.pile.focus_position = 2

    def do_select(self, source_relname, tgt_service_name,
                  tgt_relation_name):
        self.placement_controller.toggle_relation(self.service.service_name,
                                                  source_relname,
                                                  tgt_service_name,
                                                  tgt_relation_name)
        self.update()

    def sort_relation_widgets(self):
        def keyfunc(rw):
            return str(rw.reltype) + rw.source_relname
        self.relation_widgets.sort(key=keyfunc)

        def wrappedkeyfunc(t):
            rw, options = t
            if isinstance(rw, RelationWidget):
                return keyfunc(rw)
            if isinstance(rw, NoRelationWidget):
                return 'z' + keyfunc(rw)
            return 'A'

        self.pile.contents.sort(key=wrappedkeyfunc)
