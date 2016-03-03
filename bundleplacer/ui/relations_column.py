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

from urwid import (AttrMap, Button, Columns, Divider, Pile, Text,
                   WidgetWrap)

from bundleplacer.async import submit

from ubuntui.widgets.buttons import MenuSelectButton

import q

import logging

log = logging.getLogger('bundleplacer')


class RelationType(Enum):
    Requires = 0
    Provides = 1


class RelationWidget(WidgetWrap):

    def __init__(self, relation_name, interface, reltype, select_cb,
                 charm_name=None):
        self.relation_name = relation_name
        self.interface = interface
        self.reltype = reltype
        self.select_cb = select_cb
        self.is_selected = False
        self.charm_name = charm_name
        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def build_widgets(self):
        rs = str(self.reltype.name).lower()
        title = "{} ({} interface '{}')".format(self.relation_name,
                                                rs,
                                                self.interface)
        if self.charm_name:
            title = "{}".format(self.charm_name, title)
        self.button = MenuSelectButton(title,
                                       on_press=self.do_select)
        return self.button

    def update(self):
        if self.is_selected:
            self._w = AttrMap(self.button, 'deploy_highlight_start',
                              'button_secondary focus')
        else:
            self._w = AttrMap(self.button, 'text',
                              'button_secondary focus')

    def do_select(self, sender):
        self.is_selected = not self.is_selected
        self.select_cb(self, self.relation_name, self.interface,
                       selected=self.is_selected)


class RelationController:

    def __init__(self, charms):
        self.charms = charms
        # charm_name : charm_metadata        
        self.charm_info = {}
        self.metadata_future = None
        self.metadata_future_lock = RLock()
        self.charms_providing_iface = defaultdict(list)
        self.charms_requiring_iface = defaultdict(list)
        
        self.load([c.charm_name for c in self.charms])

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
            rd = md["Requires"]
            pd = md["Provides"]
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

    def handle_search_error(self, e):
        pass                    # TODO MMCC


class RelationsColumn(WidgetWrap):

    """UI to edit relations of a charm
    """

    def __init__(self, display_controller, placement_controller,
                 placement_view):
        self.placement_controller = placement_controller
        charms = placement_controller.charm_classes()
        self.rel_controller = RelationController(charms)
        self.charm = None
        self.provides = set()
        self.requires = set()
        self.placement_view = placement_view
        self.selected_iface = None
        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def build_widgets(self):
        self.title = Text(('body', "Charm added. Edit relations:"),
                          align='center')
        self.my_title = Text(('body', "Relations "), align='center')

        self.my_relations = Pile([Divider(),
                                  self.my_title])
        self.their_title = Text(('body', ""), align='center')
        self.their_relations = Pile([Divider(),
                                     self.their_title])

        self.columns = Columns([self.my_relations,
                                self.their_relations],
                               dividechars=2)
        # TODO MMCC need a "done" button,
        self.pile = Pile([Divider(), Divider(), self.title, self.columns])
        return self.pile

    def set_charm(self, charm_name):
        self.rel_controller.add_charm(charm_name)
        self.charm = next((c for c in self.controller.charm_classes()
                           if c.charm_name == charm_name), None)
    
    def update(self):
        if self.charm is None:
            return

        self.my_title.set_text(('body', "Relations "
                                "for {}".format(self.charm.charm_name)))

        p = set(self.rel_controller.get_provides(self.charm.charm_name))
        r = set(self.rel_controller.get_requires(self.charm.charm_name))
        new_p = p - self.provides
        self.provides.update(p)
        new_r = r - self.requires
        self.requires.update(r)

        if len(self.provides) + len(self.requires) == 0:
            self.title.set_text(('body', "{} added. Loading "
                                 "Relations...".format(self.charm.charm_name)))
        else:
            self.title.set_text(('body', "{} added. Select "
                                 "relations:".format(self.charm.charm_name)))
            
        for relname, iface in sorted(new_p):
            mrw = RelationWidget(relname, iface, RelationType.Provides,
                                 self.select_mine)
            self.my_relations.contents.append((mrw,
                                               self.my_relations.options()))
        for relname, iface in sorted(new_r):
            mrw = RelationWidget(relname, iface, RelationType.Requires,
                                 self.select_mine)
            self.my_relations.contents.append((mrw,
                                               self.my_relations.options()))

        # TODO MMCC: can't seem to select the column with theirs...
        iface = None
        if self.selected_iface:
            iface = self.selected_iface
            cur_w = self.selected_widget
        elif (self.columns.focus_position == 0 and
              self.my_relations.focus_position >= 2):
            cur_w = self.my_relations.focus
            if isinstance(cur_w, RelationWidget):
                iface = cur_w.interface

        if iface:
            if cur_w.reltype == RelationType.Requires:
                cs = self.rel_controller.charms_providing_iface[iface]
                verb = "provide"
                present_participle = "providing"
            else:
                cs = self.rel_controller.charms_requiring_iface[iface]
                verb = "require"
                present_participle = "requiring"
                
            theirs = [RelationWidget(relname, iface,
                                     RelationType.Provides,
                                     self.select_theirs,
                                     charm_name=charm_name) for
                      (relname, charm_name) in cs]
            if len(theirs) > 0:
                self.their_title.set_text("Charms {} {}".format(
                    present_participle, iface))
            else:
                self.their_title.set_text("No charms in this bundle "
                                          "{} {}".format(verb, iface))
                
            opts = self.their_relations.options()
            self.their_relations.contents[2:] = [(w, opts)
                                                 for w in theirs]

        for w, _ in self.my_relations.contents[2:]:
            w.update()

        for w, _ in self.their_relations.contents[2:]:
            w.update()

    def focus_prev_or_top(self):
        self.pile.focus_position = len(self.pile.contents) - 1
        self.columns.focus_position = 1
        if len(self.their_relations.contents) <= 2:
            return
        pos = self.their_relations.focus_position
        if pos < 2:
            self.their_relations.focus_position = 2

    def select_mine(self, widget, name, interface, selected):
        for w, _ in self.my_relations.contents:
            if isinstance(w, RelationWidget):
                if not selected or w.interface != interface:
                    w.is_selected = False
                    w.update()
        if selected:
            self.selected_relation_name = name
            self.selected_iface = interface
            self.selected_widget = widget
        else:
            self.selected_relation_name = None
            self.selected_iface = None
            self.selected_widget = None
        if len(self.their_relations.contents) > 2:
            self.focus_theirs()
        self.update()

    def select_theirs(self, their_charm_name, their_relation_name):
        self.controller.add_relation(self.charm,
                                     self.selected_relation_name,
                                     their_charm_name,
                                     their_relation_name)
