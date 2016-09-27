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

from urwid import AttrMap, Columns, Divider, Pile, Text, WidgetWrap

from bundleplacer.assignmenttype import AssignmentType
from ubuntui.widgets.buttons import MenuSelectButton, PlainButton

log = logging.getLogger('bundleplacer')


class SimpleMachineWidget(WidgetWrap):

    """A widget displaying a machine. When selected, shows action buttons
    for placement types.

    machine - the machine to display

    controller - a PlacementController instance

    display_controller - a PlacerView instance

    show_assignments - display info about which charms are assigned
    and what assignment type (LXC, KVM, etc) they have.

    """

    def __init__(self, machine, controller,
                 display_controller, show_assignments=True):
        self.machine = machine
        self.controller = controller
        self.display_controller = display_controller
        self.show_assignments = show_assignments
        self.is_selected = False
        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def build_widgets(self):

        self.button = MenuSelectButton("I AM A MACHINE", self.do_select)
        self.action_button_cols = Columns([])
        self.action_buttons = []

        self.pile = Pile([self.button])
        return self.pile

    def update_machine(self):
        """Refresh with potentially updated machine info from controller.
        Assumes that machine exists - machines going away is handled
        in machineslist.update().
        """
        self.machine = next((m for m in self.controller.machines()
                             if m.instance_id == self.machine.instance_id),
                            None)

    def update(self):
        self.update_machine()
        self.update_action_buttons()

        if self.is_selected:
            self.update_selected()
        else:
            self.update_unselected()

    def info_markup(self):
        m = self.machine
        return [self.machine.hostname + "\n",
                'arch: {}  '.format(m.arch),
                'cores: {}  '.format(m.cpu_cores),
                'mem: {}  '.format(m.mem),
                'storage: {}'.format(m.storage)]

    def update_selected(self):
        cn = self.display_controller.selected_service.service_name
        msg = Text("  Add {} to {}:".format(cn,
                                            self.machine.hostname))
        self.pile.contents = [(msg, self.pile.options()),
                              (self.action_button_cols,
                               self.pile.options()),
                              (Divider(), self.pile.options())]

    def update_unselected(self):
        markup = self.info_markup()
        self.button.set_label(markup)
        self.pile.contents = [(AttrMap(self.button, 'text',
                                       'button_secondary focus'),
                               self.pile.options()),
                              (Divider(), self.pile.options())]

    def update_action_buttons(self):

        all_actions = [(AssignmentType.BareMetal,
                        'Add as Bare Metal',
                        self.select_baremetal),
                       (AssignmentType.LXD,
                        'Add as LXD',
                        self.select_lxd),
                       (AssignmentType.KVM,
                        'Add as KVM',
                        self.select_kvm)]

        sc = self.display_controller.selected_service
        if sc:
            allowed_set = set(sc.allowed_assignment_types)
            allowed_types = set([atype for atype, _, _ in all_actions])
            allowed_types = allowed_types.intersection(allowed_set)
        else:
            allowed_types = set()

        # + 1 for the cancel button:
        if len(self.action_buttons) == len(allowed_types) + 1:
            return

        self.action_buttons = [AttrMap(PlainButton(label,
                                                   on_press=func),
                                       'button_secondary',
                                       'button_secondary focus')
                               for atype, label, func in all_actions
                               if atype in allowed_types]
        self.action_buttons.append(
            AttrMap(PlainButton("Cancel",
                                on_press=self.do_cancel),
                    'button_secondary',
                    'button_secondary focus'))

        opts = self.action_button_cols.options()
        self.action_button_cols.contents = [(b, opts) for b in
                                            self.action_buttons]

    def do_select(self, sender):
        if self.display_controller.selected_service is None:
            return
        self.is_selected = True
        self.update()
        self.pile.focus_position = 1
        self.action_button_cols.focus_position = 0

    def do_cancel(self, sender):
        self.is_selected = False
        self.update()
        self.pile.focus_position = 0

    def _do_select_assignment(self, atype):
        {AssignmentType.BareMetal:
         self.display_controller.do_select_baremetal,
         AssignmentType.LXD:
         self.display_controller.do_select_lxd,
         AssignmentType.KVM:
         self.display_controller.do_select_kvm}[atype](self.machine)
        self.pile.focus_position = 0

    def select_baremetal(self, sender):
        self._do_select_assignment(AssignmentType.BareMetal)

    def select_lxd(self, sender):
        self._do_select_assignment(AssignmentType.LXD)

    def select_kvm(self, sender):
        self._do_select_assignment(AssignmentType.KVM)
