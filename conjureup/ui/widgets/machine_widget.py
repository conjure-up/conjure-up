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
import logging

from urwid import AttrMap, Columns, Divider, Pile, Text, WidgetWrap

from bundleplacer.assignmenttype import AssignmentType, atype_to_label
from conjureup.app_config import app
from ubuntui.widgets.buttons import PlainButton

log = logging.getLogger('bundleplacer')


class MachineWidget(WidgetWrap):

    """A widget displaying a machine and one action button.

    machine - the machine to display

    select_cb - a function that takes a machine to select

    unselect_cb - a function that takes a machine to un-select

    context_string - a string to show in the label for context

    """

    def __init__(self, machine, select_cb, unselect_cb,
                 context_string):
        self.machine = machine
        self.is_selected = False
        self.select_cb = select_cb
        self.unselect_cb = unselect_cb
        self.context_string = context_string
        self.can_select = True

        w = self.build_widgets()
        super().__init__(w)

    def selectable(self):
        return True

    def build_widgets(self):
        m = self.machine
        l = ['{:20s}'.format(m.hostname),
             '{:3d}'.format(m.cpu_cores),
             '{:6s}'.format(m.mem),
             '{:10s}'.format(m.storage)]

        self.select_button_label = "Pin {} to {}".format(m.hostname,
                                                         self.context_string)
        self.unselect_button_label = "Un-pin {} from {}".format(
            m.hostname, self.context_string)

        self.select_button = PlainButton(self.select_button_label,
                                         self.handle_button)
        cols = [Text(m) for m in l]

        if self.can_select:
            cols += [AttrMap(self.select_button, 'text',
                             'button_secondary focus')]
        else:
            cols.append(Text(""))

        self.columns = Columns(cols)
        return self.columns

    def update_machine(self):
        """Refresh with potentially updated machine info from controller.
        Assumes that machine exists - machines going away is handled
        in machineslist.update().
        """
        self.machine = next((m for m in app.maas.client.get_machines()
                             if m.instance_id == self.machine.instance_id),
                            None)

    def __repr__(self):
        return "widget for " + str(self.machine)

    def update(self):
        self.update_machine()
        if self.is_selected:
            self.select_button.set_label(self.unselect_button_label)
        else:
            self.select_button.set_label(self.select_button_label)

        opts = self.columns.options()
        if self.can_select:
            self.columns.contents[-1] = (self.select_button,
                                         opts)
        else:
            self.columns.contents[-1] = (Text(""), opts)

    def handle_button(self, sender):
        if self.is_selected:
            self.is_selected = False
            self.unselect_cb(self.machine)
        else:
            self.is_selected = True
            self.select_cb(self.machine)

        self.update()
