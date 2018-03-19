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

from bundleplacer.assignmenttype import AssignmentType, atype_to_label
from urwid import (
    AttrMap,
    Columns,
    Divider,
    Edit,
    IntEdit,
    Pile,
    Text,
    connect_signal
)

from conjureup import juju, units
from conjureup.ui.widgets.base import ContainerWidgetWrap
from conjureup.ui.widgets.buttons import SecondaryButton


class JujuMachineWidget(ContainerWidgetWrap):

    """A widget displaying a machine and action buttons.

    juju_machine_id = juju id of the machine

    md = the machine dict

    application - the current application for which machines are being shown

    assign_cb - a function that takes a machine and assignmenttype to
    perform the button action

    unassign_cb - a function that takes a machine and removes
    assignments for the machine

    controller - a controller object that provides show_pin_chooser

    show_assignments - display info about which charms are assigned
    and what assignment type (LXC, KVM, etc) they have.

    show_pin - show button to pin juju machine to a maas machine

    """

    def __init__(self, juju_machine_id, md, application, assign_cb,
                 unassign_cb, controller, show_assignments=True,
                 show_pin=False):
        self.juju_machine_id = juju_machine_id
        self.md = md
        self.application = application
        self.is_selected = False
        self.assign_cb = assign_cb
        self.unassign_cb = unassign_cb
        self.controller = controller
        self.show_assignments = show_assignments
        self.show_pin = show_pin
        self.all_assigned = False

        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def __repr__(self):
        return "jujumachinewidget #" + str(self.juju_machine_id)

    def build_widgets(self):

        self.action_button_cols = Columns([])
        self.action_buttons = []
        self.build_unselected_widgets()
        self.pile = Pile([self.unselected_columns])
        return self.pile

    def build_unselected_widgets(self):
        cdict = juju.constraints_to_dict(self.md.get('constraints', ''))

        label = str(self.juju_machine_id)
        self.juju_machine_id_button = SecondaryButton(label,
                                                      self.show_pin_chooser)
        self.juju_machine_id_label = Text(label)
        self.cores_field = IntEdit('', str(cdict.get('cores', '')))
        connect_signal(self.cores_field, 'change', self.handle_cores_changed)
        memval = cdict.get('mem', '')
        if memval != '':
            memval = self._format_constraint(memval) / 1024
        self.mem_field = Edit('', str(memval))
        connect_signal(self.mem_field, 'change', self.handle_mem_changed)
        diskval = cdict.get('root-disk', '')
        if diskval != '':
            diskval = self._format_constraint(diskval) / 1024
        self.disk_field = Edit('', str(diskval))
        connect_signal(self.disk_field, 'change', self.handle_disk_changed)

        if self.show_pin:
            machine_id_w = self.juju_machine_id_button
        else:
            machine_id_w = self.juju_machine_id_label
        cols = [machine_id_w]
        for field in (self.cores_field, self.mem_field, self.disk_field):
            cols.append(AttrMap(field, 'string_input', 'string_input_focus'))
        cols.append(Text("placeholder"))
        self.unselected_columns = Columns(cols, dividechars=2)
        self.update_assignments()
        return self.unselected_columns

    def update_assignments(self):
        assignments = []

        mps = self.controller.get_all_assignments(self.juju_machine_id)
        if len(mps) > 0:
            if self.show_assignments:
                ad = defaultdict(list)
                for application, atype in mps:
                    ad[atype].append(application)
                astr = " ".join(["{}{}".format(
                    atype_to_label([atype])[0],
                    ",".join([application.service_name
                              for application in al]))
                    for atype, al in ad.items()])
                assignments.append(astr)
        else:
            if self.show_assignments:
                assignments.append("-")

        if any([application == self.application for application, _ in mps]):
            action = self.do_remove
            label = "Remove"
        else:
            action = self.do_select
            label = "Select"

        self.select_button = SecondaryButton(label, action)

        cols = [Text(s) for s in assignments]

        current_assignments = [a for a, _ in mps if a == self.application]
        if self.all_assigned and len(current_assignments) == 0:
            cols.append(Text(""))
        else:
            cols.append(self.select_button)
        opts = self.unselected_columns.options()
        self.unselected_columns.contents[4:] = [(w, opts) for w in cols]

    def update(self):
        self.update_action_buttons()

        if self.is_selected:
            self.update_selected()
        else:
            self.update_unselected()

    def update_selected(self):
        cn = self.application.service_name
        msg = Text("  Add {} to machine #{}:".format(cn,
                                                     self.juju_machine_id))
        self.pile.contents = [(msg, self.pile.options()),
                              (self.action_button_cols,
                               self.pile.options()),
                              (Divider(), self.pile.options())]

    def update_unselected(self):
        if self.show_pin:
            pinned_machine = self.controller.get_pin(self.juju_machine_id)

            if pinned_machine:
                label = "{} \N{RIGHTWARDS ARROW}  {}".format(
                    self.juju_machine_id, pinned_machine.hostname)
            else:
                label = str(self.juju_machine_id)
            label = "\N{PENCIL}  {}".format(label)
            self.juju_machine_id_button.set_label(label)
        else:
            self.juju_machine_id_label.set_text(str(self.juju_machine_id))

        self.pile.contents = [(self.unselected_columns, self.pile.options()),
                              (Divider(), self.pile.options())]
        self.update_assignments()

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

        self.action_buttons = [SecondaryButton(label, func)
                               for atype, label, func in all_actions
                               if atype in allowed_types]
        self.action_buttons.append(SecondaryButton("Cancel",
                                                   self.do_cancel))

        opts = self.action_button_cols.options()
        self.action_button_cols.contents = [(b, opts) for b in
                                            self.action_buttons]

    def do_select(self, sender):
        self.is_selected = True
        self.update()
        self.pile.focus_position = 1
        self.action_button_cols.focus_position = 0

    def do_remove(self, sender):
        self.unassign_cb(self.juju_machine_id)

    def do_cancel(self, sender):
        self.is_selected = False
        self.update()
        self.pile.focus_position = 0

    def _do_select_assignment(self, atype):
        self.assign_cb(self.juju_machine_id, atype)
        self.pile.focus_position = 0
        self.is_selected = False
        self.update()

    def select_baremetal(self, sender):
        self._do_select_assignment(AssignmentType.BareMetal)

    def select_lxd(self, sender):
        self._do_select_assignment(AssignmentType.LXD)

    def select_kvm(self, sender):
        self._do_select_assignment(AssignmentType.KVM)

    def handle_cores_changed(self, sender, val):
        if val == '':
            self.md = self.controller.clear_constraint(self.juju_machine_id,
                                                       'cores')
        else:
            self.md = self.controller.set_constraint(self.juju_machine_id,
                                                     'cores', val)

    def _format_constraint(self, val):
        "Store constraints as int values of megabytes"
        if val.isnumeric():
            return int(val) * 1024
        else:
            return units.human_to_mb(val)

    def handle_mem_changed(self, sender, val):
        if val == '':
            self.md = self.controller.clear_constraint(self.juju_machine_id,
                                                       'mem')
        else:
            try:
                self.md = self.controller.set_constraint(
                    self.juju_machine_id, 'mem',
                    self._format_constraint(val))
            except ValueError:
                return

    def handle_disk_changed(self, sender, val):
        if val == '':
            self.md = self.controller.clear_constraint(self.juju_machine_id,
                                                       'root-disk')
        else:
            try:
                self.md = self.controller.set_constraint(
                    self.juju_machine_id, 'root-disk',
                    self._format_constraint(val))
            except ValueError:
                return

    def show_pin_chooser(self, sender):
        self.controller.show_pin_chooser(self.juju_machine_id)
