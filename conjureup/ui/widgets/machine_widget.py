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
from ubuntui.widgets.buttons import MenuSelectButton, PlainButton

log = logging.getLogger('bundleplacer')


class MachineWidget(WidgetWrap):

    """A widget displaying a machine and action buttons.

    machine - the machine to display

    application - the current application for which machines are being shown

    select_cb - a function that takes a machine and assignmenttype to
    perform the button action

    unselect_cb - a function that takes a machine and removes
    assignments for the machine

    show_assignments - display info about which charms are assigned
    and what assignment type (LXC, KVM, etc) they have.

    """

    def __init__(self, machine, application, select_cb, unselect_cb,
                 controller, show_assignments=True):
        self.machine = machine
        self.application = application
        self.is_selected = False
        self.select_cb = select_cb
        self.unselect_cb = unselect_cb
        self.controller = controller
        self.show_assignments = show_assignments
        self.all_assigned = False

        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def build_widgets(self):

        self.action_button_cols = Columns([])
        self.action_buttons = []

        self.pile = Pile([self.get_toprow()])
        return self.pile

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

    def get_toprow(self):
        m = self.machine
        l = ['{:20s}'.format(m.hostname),
             '{:3d}'.format(m.cpu_cores),
             '{:6s}'.format(m.mem),
             '{:10s}'.format(m.storage)]

        mps = self.controller.get_placements(self.application, m)
        if len(mps) > 0:
            if self.show_assignments:
                ad = defaultdict(list)
                for application, atype in mps:
                    ad[atype].append(application)
                astr = " ".join(["{}{}".format(atype_to_label(atype),
                                               ",".join([a.service_name
                                                         for a in al]))
                                 for atype, al in ad.items()])
                l.append(astr)
            action = self.do_remove
            label = "Remove"
        else:
            if self.show_assignments:
                l.append("-")
            action = self.do_select
            label = "Select"

        select_button = MenuSelectButton(label, action)
        cols = [Text(m) for m in l]

        current_assignments = [a for a, _ in mps if a == self.application]
        if self.all_assigned and len(current_assignments) == 0:
            cols.append(Text(""))
        else:
            cols += [AttrMap(select_button, 'text',
                             'button_secondary focus')]
        return Columns(cols)

    def update(self):
        self.update_machine()
        self.update_action_buttons()

        if self.is_selected:
            self.update_selected()
        else:
            self.update_unselected()

    def update_selected(self):
        cn = self.application.service_name
        msg = Text("  Add {} to {}:".format(cn,
                                            self.machine.hostname))
        self.pile.contents = [(msg, self.pile.options()),
                              (self.action_button_cols,
                               self.pile.options()),
                              (Divider(), self.pile.options())]

    def update_unselected(self):
        self.pile.contents = [(self.get_toprow(), self.pile.options()),
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

        sc = self.application
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
        self.is_selected = True
        self.update()
        self.pile.focus_position = 1
        self.action_button_cols.focus_position = 0

    def do_remove(self, sender):
        self.controller.remove_placement(self.application, self.machine)
        self.unselect_cb(self.machine)

    def do_cancel(self, sender):
        self.is_selected = False
        self.update()
        self.pile.focus_position = 0

    def _do_select_assignment(self, atype):
        self.controller.add_placement(self.application, self.machine, atype)
        self.select_cb(self.machine, atype)
        self.pile.focus_position = 0
        self.is_selected = False
        self.update()

    def select_baremetal(self, sender):
        self._do_select_assignment(AssignmentType.BareMetal)

    def select_lxd(self, sender):
        self._do_select_assignment(AssignmentType.LXD)

    def select_kvm(self, sender):
        self._do_select_assignment(AssignmentType.KVM)
