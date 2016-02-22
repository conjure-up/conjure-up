# Copyright 2015 Canonical, Ltd.
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


from urwid import (AttrMap, Button, Divider, GridFlow, LineBox, Pile,
                   Text, WidgetWrap)

from bundleplacer.ui.machine_widget import MachineWidget
from bundleplacer.ui.services_list import ServicesList


class ServiceChooser(WidgetWrap):

    """Presents list of services to put on a machine.

    Supports multiple selection, implying separate containers using
    --to.

    """

    def __init__(self, controller, machine, parent_widget):
        """
        controller is a PlacementController
        machine is the machine to show Services for
        parent_widget should support 'remove_overlay()'
        """
        self.controller = controller
        self.machine = machine
        self.parent_widget = parent_widget
        w = self.build_widgets()
        super().__init__(w)

    def build_widgets(self):

        instructions = Text("Remove services from {}".format(
            self.machine.hostname))

        self.machine_widget = MachineWidget(self.machine,
                                            self.controller,
                                            show_hardware=True)

        def show_remove_p(cc):
            md = self.controller.get_assignments(cc)
            for atype, ms in md.items():
                hostnames = [m.hostname for m in ms]
                if self.machine.hostname in hostnames:
                    return True
            return False

        actions = [(show_remove_p, 'Remove', self.do_remove)]

        self.services_list = ServicesList(self.controller,
                                          actions, actions,
                                          machine=self.machine)

        close_button = AttrMap(Button('X',
                                      on_press=self.close_pressed),
                               'button_secondary', 'button_secondary focus')
        p = Pile([GridFlow([close_button], 5, 1, 0, 'right'),
                  instructions, Divider(), self.machine_widget,
                  Divider(), self.services_list])

        return LineBox(p, title="Remove Services")

    def update(self):
        self.machine_widget.update()
        self.services_list.update()

    def do_add(self, sender, charm_class, atype):
        self.controller.assign(self.machine, charm_class, atype)
        self.update()

    def do_remove(self, sender, charm_class):
        self.controller.remove_one_assignment(self.machine,
                                              charm_class)
        self.update()

    def close_pressed(self, sender):
        self.parent_widget.remove_overlay(self)
