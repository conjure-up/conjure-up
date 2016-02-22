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


from urwid import (AttrMap, Button, Divider, GridFlow, Padding, Pile,
                   SelectableIcon, Text, WidgetWrap)

from bundleplacer.assignmenttype import AssignmentType


class MachineWidget(WidgetWrap):

    """A widget displaying a service and associated actions.

    machine - the machine to display

    controller - a PlacementController instance

    actions - a list of ('label', function) pairs that wil be used to
    create buttons for each machine.  The machine will be passed to
    the function as userdata.

    optionally, actions can be a 3-tuple (pred, 'label', function),
    where pred determines whether to add the button. Pred will be
    passed the charm class.

    show_hardware - display hardware details about this machine

    show_assignments - display info about which charms are assigned
    and what assignment type (LXC, KVM, etc) they have.
    """

    def __init__(self, machine, controller, actions=None,
                 show_hardware=False, show_assignments=True):
        self.machine = machine
        self.controller = controller
        if actions is None:
            self.actions = []
        else:
            self.actions = actions
        self.show_hardware = show_hardware
        self.show_assignments = show_assignments
        w = self.build_widgets()
        self.update()
        super().__init__(w)

    def selectable(self):
        return True

    def hardware_info_markup(self):
        m = self.machine
        return [('label', 'arch'), ' {}  '.format(m.arch),
                ('label', 'cores'), ' {}  '.format(m.cpu_cores),
                ('label', 'mem'), ' {}  '.format(m.mem),
                ('label', 'storage'), ' {}'.format(m.storage)]

    def build_widgets(self):

        self.machine_info_widget = Text("")
        self.assignments_widget = Text("")
        self.hardware_widget = Text("")

        self.buttons = []
        self.button_grid = GridFlow(self.buttons, 22, 1, 1, 'right')

        pl = [Divider(' '), self.machine_info_widget]
        if self.show_hardware:
            pl.append(self.hardware_widget)
        if self.show_assignments:
            pl += [Divider(' '), self.assignments_widget]
        pl.append(self.button_grid)

        p = Pile(pl)

        return Padding(p, left=2, right=2)

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
        if self.machine == self.controller.sub_placeholder:
            self.machine_info_widget.set_text("\N{BULLET} Subordinate Charms")
            self.hardware_widget.set_text("")
        elif self.machine == self.controller.def_placeholder:
            self.machine_info_widget.set_text("\N{BULLET} Juju Default "
                                              "Placement")
            self.hardware_widget.set_text("")
        else:
            info_markup = ["\N{TAPE DRIVE} {}".format(self.machine.hostname),
                           ('label', " ({})".format(self.machine.status))]
            self.machine_info_widget.set_text(info_markup)
            self.hardware_widget.set_text(["  "] + self.hardware_info_markup())

        ad = self.controller.assignments_for_machine(self.machine)
        astr = [('label', "  Services: ")]

        for atype, al in ad.items():
            n = len(al)
            if n == 1:
                pl_s = ""
            else:
                pl_s = "s"
            if atype == AssignmentType.BareMetal:
                astr.append(('label', "\n    {} service{}"
                             " on Bare Metal: ".format(n, pl_s)))
            else:
                astr.append(('label', "\n    {} "
                             "{}{}: ".format(n, atype.name, pl_s)))
            if n == 0:
                astr.append("\N{EMPTY SET}")
            else:
                astr.append(", ".join(["\N{GEAR} {}".format(c.display_name)
                                       for c in al]))

        if self.machine == self.controller.sub_placeholder:
            assignments_text = ''
            for _, al in ad.items():
                charm_txts = ["\N{GEAR} {}".format(c.display_name)
                              for c in al]
                assignments_text += ", ".join(charm_txts)
        else:
            assignments_text = astr

        self.assignments_widget.set_text(assignments_text)
        self.update_buttons()

    def update_buttons(self):
        buttons = []
        for at in self.actions:
            if len(at) == 2:
                def predicate(x):
                    return True
                label, func = at
            else:
                predicate, label, func = at

            if not predicate(self.machine):
                b = AttrMap(SelectableIcon(" (" + label + ")"),
                            'disabled_button', 'disabled_button_focus')
            else:
                b = AttrMap(Button(label, on_press=func,
                                   user_data=self.machine),
                            'button_secondary', 'button_secondary focus')
            buttons.append((b, self.button_grid.options()))

        self.button_grid.contents = buttons
