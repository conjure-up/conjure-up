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

import logging

from urwid import Divider, Pile, Text, WidgetWrap

from bundleplacer.maas import MaasMachineStatus, satisfies
from bundleplacer.ui.filter_box import FilterBox
from bundleplacer.ui.simple_machine_widget import SimpleMachineWidget

log = logging.getLogger('bundleplacer')


class MachinesList(WidgetWrap):

    """A list of machines with configurable action buttons for each
    machine.

    action - a function to call when the machine's button is pressed

    constraints - a dict of constraints to filter the machines list.
    only machines matching all the constraints will be shown.

    show_hardware - bool, whether or not to show the hardware details
    for each of the machines

    title_widgets - A Text Widget to be used in place of the default
    title.

    show_assignments - bool, whether or not to show the assignments
    for each of the machines.

    show_only_ready - bool, only show machines with a ready state.

    """

    def __init__(self, controller, display_controller,
                 constraints=None, show_hardware=False,
                 title_widgets=None, show_assignments=True,
                 show_placeholders=True, show_only_ready=False,
                 show_filter_box=False):
        self.controller = controller
        self.display_controller = display_controller
        self.machine_widgets = []
        if constraints is None:
            self.constraints = {}
        else:
            self.constraints = constraints
        self.show_hardware = show_hardware
        self.show_assignments = show_assignments
        self.show_placeholders = show_placeholders
        self.show_only_ready = show_only_ready
        self.show_filter_box = show_filter_box
        self.filter_string = ""
        w = self.build_widgets(title_widgets)
        self.update()
        super().__init__(w)

    def selectable(self):
        # overridden to ensure that we can arrow through the buttons
        # shouldn't be necessary according to documented behavior of
        # Pile & Columns, but discovered via trial & error.
        return True

    def build_widgets(self, title_widgets):
        if title_widgets is None:
            if len(self.constraints) > 0:
                cstr = " matching constraints"
            else:
                cstr = ""

            title_widgets = [Text("Machines" + cstr, align='center')]

        self.filter_edit_box = FilterBox(self.handle_filter_change)

        header_widgets = title_widgets + [Divider()]

        if self.show_filter_box:
            header_widgets.append(self.filter_edit_box)

        self.header_padding = len(header_widgets)
        self.machine_pile = Pile(header_widgets + self.machine_widgets)
        return self.machine_pile

    def handle_filter_change(self, edit_button, userdata):
        self.filter_string = userdata
        self.update()

    def find_machine_widget(self, m):
        return next((mw for mw in self.machine_widgets if
                     mw.machine.instance_id == m.instance_id), None)

    def update(self):
        machines = self.controller.machines(
            include_placeholders=self.show_placeholders)
        if self.show_only_ready:
            machines = [m for m in machines
                        if m.status == MaasMachineStatus.READY]
        for mw in self.machine_widgets:
            machine = next((m for m in machines if
                            mw.machine.instance_id == m.instance_id), None)
            if machine is None:
                self.remove_machine(mw.machine)

        n_satisfying_machines = len(machines)

        def get_placement_filter_label(d):
            s = ""
            for atype, al in d.items():
                s += " ".join(["{} {}".format(cc.service_name,
                                              cc.display_name)
                               for cc in al])
            return s

        for m in machines:
            if not satisfies(m, self.constraints)[0]:
                self.remove_machine(m)
                n_satisfying_machines -= 1
                continue

            assignment_names = ""
            ad = self.controller.assignments_for_machine(m)
            assignment_names = get_placement_filter_label(ad)
            filter_label = "{} {}".format(m.filter_label(),
                                          assignment_names)
            if self.filter_string != "" and \
               self.filter_string not in filter_label:
                self.remove_machine(m)
                continue

            mw = self.find_machine_widget(m)
            if mw is None:
                mw = self.add_machine_widget(m)
            mw.update()

        self.filter_edit_box.set_info(len(self.machine_widgets),
                                      n_satisfying_machines)

        self.sort_machine_widgets()

    def add_machine_widget(self, machine):
        mw = SimpleMachineWidget(machine,
                                 self.controller,
                                 self.display_controller,
                                 self.show_assignments)
        self.machine_widgets.append(mw)
        options = self.machine_pile.options()
        self.machine_pile.contents.append((mw, options))

        # NOTE: see the +1: indexing in remove_machine if you re-add
        # this divider. it should then be +2.

        # self.machine_pile.contents.append((AttrMap(Padding(Divider('\u23bc'),
        #                                                    left=2, right=2),
        #                                            'label'), options))
        return mw

    def remove_machine(self, machine):
        mw = self.find_machine_widget(machine)
        if mw is None:
            return

        self.machine_widgets.remove(mw)
        mw_idx = 0
        for w, opts in self.machine_pile.contents:
            if w == mw:
                break
            mw_idx += 1

        c = self.machine_pile.contents[:mw_idx] + \
            self.machine_pile.contents[mw_idx + 1:]
        self.machine_pile.contents = c

    def sort_machine_widgets(self):
        def keyfunc(mw):
            m = mw.machine
            hwinfo = " ".join(map(str, [m.arch, m.cpu_cores, m.mem,
                                        m.storage]))
            if str(mw.machine.status) == 'ready':
                skey = 'A'
            else:
                skey = str(mw.machine.status)
            return skey + mw.machine.hostname + hwinfo
        self.machine_widgets.sort(key=keyfunc)

        def wrappedkeyfunc(t):
            mw, options = t
            if not isinstance(mw, SimpleMachineWidget):
                return 'A'
            return keyfunc(mw)

        self.machine_pile.contents.sort(key=wrappedkeyfunc)

    def focus_prev_or_top(self):
        self.update()
        try:
            if self.machine_pile.focus_position <= self.header_padding:
                self.machine_pile.focus_position = self.header_padding
        except IndexError:
            log.debug("index error in machines_list focus_top")
