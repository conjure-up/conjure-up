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

from bundleplacer.assignmenttype import AssignmentType

from bundleplacer.ui.service_widget import ServiceWidget
from bundleplacer.ui.machines_list import MachinesList

import logging

log = logging.getLogger('bundleplacer')


class MachineChooser(WidgetWrap):

    """Presents list of machines to assign a service to.
    Supports multiple selection if the service does.
    """

    def __init__(self, controller, charm_class, parent_widget):
        self.controller = controller
        self.charm_class = charm_class
        self.parent_widget = parent_widget
        w = self.build_widgets()
        super().__init__(w)

    def build_widgets(self):

        if self.charm_class.allow_multi_units:
            machine_string = "machines"
            plural_string = "s"
        else:
            machine_string = "a machine"
            plural_string = ""
        instructions = Text("Select {} to host {}".format(
            machine_string, self.charm_class.display_name))

        self.service_widget = ServiceWidget(self.charm_class,
                                            self.controller,
                                            show_constraints=True,
                                            show_placements=True)

        all_actions = [(AssignmentType.BareMetal,
                        'Add as Bare Metal',
                        self.do_select_baremetal),
                       (AssignmentType.LXC,
                        'Add as LXC', self.do_select_lxc),
                       (AssignmentType.KVM,
                        'Add as KVM', self.do_select_kvm)]

        actions = [(label, func) for atype, label, func in all_actions
                   if atype in self.charm_class.allowed_assignment_types]

        constraints = self.charm_class.constraints
        # NOTE: show_assignments=False is a WORKAROUND for #194
        self.machines_list = MachinesList(self.controller,
                                          actions,
                                          constraints=constraints,
                                          show_hardware=True,
                                          show_assignments=False)
        self.machines_list.update()
        close_button = AttrMap(Button('X',
                                      on_press=self.close_pressed),
                               'button_secondary', 'button_secondary focus')
        p = Pile([GridFlow([close_button], 5, 1, 0, 'right'),
                  instructions, Divider(), self.service_widget,
                  Divider(), self.machines_list])

        return LineBox(p, title="Select Machine{}".format(plural_string))

    def do_select_baremetal(self, sender, machine):
        self.do_select(sender, machine, AssignmentType.BareMetal)

    def do_select_lxc(self, sender, machine):
        self.do_select(sender, machine, AssignmentType.LXC)

    def do_select_kvm(self, sender, machine):
        self.do_select(sender, machine, AssignmentType.KVM)

    def do_select(self, sender, machine, atype):
        self.controller.assign(machine, self.charm_class, atype)
        self.machines_list.update()
        self.service_widget.update()
        self.parent_widget.remove_overlay(self)

    def close_pressed(self, sender):
        self.parent_widget.remove_overlay(self)
