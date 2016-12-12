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

from urwid import AttrMap, Columns, Text, WidgetWrap

from conjureup.app_config import app
from ubuntui.widgets.buttons import PlainButton

log = logging.getLogger('bundleplacer')


class MachineWidget(WidgetWrap):

    """A widget displaying a machine and one action button.

    machine - the machine to display

    select_cb - a function that takes a machine to select

    unselect_cb - a function that takes a machine to un-select

    target_info - a string describing what we're pinning to

    current_pin_cb - a function that takes a machine and returns a
    string if it's already pinned or None if it is not

    """

    def __init__(self, machine, select_cb, unselect_cb,
                 target_info, current_pin_cb):
        self.machine = machine
        self.select_cb = select_cb
        self.unselect_cb = unselect_cb
        self.target_info = target_info
        self.current_pin_cb = current_pin_cb

        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def build_widgets(self):
        m = self.machine
        l = ['{:20s}'.format(m.hostname),
             '{:3d}'.format(m.cpu_cores),
             '{:6s}'.format(m.mem),
             '{:10s}'.format(m.storage)]

        self.select_button_label = "Pin {} to {}".format(m.hostname,
                                                         self.target_info)
        self.unselect_button_label = "Un-pin {} from ".format(
            m.hostname) + "{}"

        self.select_button = PlainButton(self.select_button_label,
                                         self.handle_button)
        cols = [Text(m) for m in l]
        cols += [AttrMap(self.select_button, 'text',
                         'button_secondary focus')]

        self.columns = Columns(cols)
        return self.columns

    def update_machine(self):
        """Refresh with potentially updated machine info from controller.
        Assumes that machine exists - machines going away is handled
        in machineslist.update().
        """
        machines = app.maas.client.get_machines()
        if machines is None:
            return
        self.machine = next((m for m in machines
                             if m.instance_id == self.machine.instance_id),
                            None)

    def __repr__(self):
        return "widget for " + str(self.machine)

    def update(self):
        self.update_machine()
        current_pin = self.current_pin_cb(self.machine)
        if current_pin:
            l = self.unselect_button_label.format(current_pin)
            self.select_button.set_label(l)
        else:
            self.select_button.set_label(self.select_button_label)

    def handle_button(self, sender):
        if self.current_pin_cb(self.machine):
            self.unselect_cb(self.machine)
        else:
            self.select_cb(self.machine)

        self.update()
