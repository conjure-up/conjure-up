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

from urwid import AttrMap, Divider, Pile, Text, WidgetWrap

from bundleplacer.relationtype import RelationType
from ubuntui.widgets.buttons import MenuSelectButton

log = logging.getLogger('bundleplacer')


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
        s = "({}: nothing in bundle {} {})".format(relname,
                                                   other_reltype.name.lower(),
                                                   iface)
        super().__init__(AttrMap(MenuSelectButton(s), 'label',
                                 'button_secondary focus'))

    def selectable(self):
        return True

    def update(self):
        "no op"


class RelationsColumn(WidgetWrap):

    """UI to edit relations of a service
    """

    def __init__(self, display_controller, placement_controller,
                 placement_view, metadata_controller):
        self.placement_controller = placement_controller
        self.metadata_controller = metadata_controller
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

    def set_service(self, service):
        self.service = service
        self.metadata_controller.add_charm(service.csid.as_str_without_rev())
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
            self.title.set_text(('body', "Edit Relations: (Changes are "
                                 "saved immediately)"))

        p = set(self.metadata_controller.get_provides(
            self.service.csid.as_str_without_rev()))
        r = set(self.metadata_controller.get_requires(
            self.service.csid.as_str_without_rev()))
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
