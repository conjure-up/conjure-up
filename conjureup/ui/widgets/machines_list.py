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
# along with this program.  If not, see <http://www.gnu.org/licenses>.

import logging

from urwid import Columns, Divider, Pile, Text, WidgetWrap

from conjureup.maas import MaasMachineStatus, satisfies
from conjureup.app_config import app
from conjureup.ui.widgets.filter_box import FilterBox
from conjureup.ui.widgets.machine_widget import MachineWidget

log = logging.getLogger('bundleplacer')


class MachinesList(WidgetWrap):

    """A list of machines with configurable action buttons for each
    machine.

    application - an application

    select_cb - a function that takes a machine and assignmenttype to
    perform the button action

    unselect_cb - a function that takes a machine and clears assignments

    controller - deploy/gui controller

    constraints - a dict of constraints to filter the machines list.
    only machines matching all the constraints will be shown.

    show_hardware - bool, whether or not to show the hardware details
    for each of the machines

    title_widgets - A Text Widget to be used in place of the default
    title.

    show_assignments - bool, whether or not to show the assignments
    for each of the machines.

    show_only_ready - bool, only show machines with a ready state.

    show_filter_box - bool, show text box to filter listed machines

    """

    def __init__(self, application, select_cb, unselect_cb,
                 controller,
                 constraints=None, show_hardware=False,
                 title_widgets=None, show_assignments=True,
                 show_only_ready=False,
                 show_filter_box=False):
        self.application = application
        self.select_cb = select_cb
        self.unselect_cb = unselect_cb
        self.controller = controller
        self.all_assigned = False
        self.machine_widgets = []
        if constraints is None:
            self.constraints = {}
        else:
            self.constraints = constraints
        self.show_hardware = show_hardware
        self.show_assignments = show_assignments
        self.show_only_ready = show_only_ready
        self.show_filter_box = show_filter_box
        self.filter_string = ""
        self.loading = False
        w = self.build_widgets(title_widgets)
        self.update()
        super().__init__(w)

    def __repr__(self):
        return "machineslist"

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
            header_widgets += [self.filter_edit_box, Divider()]
        labels = ["FQDN", "Cores", "Memory", "Storage"]
        if self.show_assignments:
            labels += ["Assignments", ""]
        else:
            labels += [""]
        header_label_col = Columns([Text(m) for m in labels])
        header_widgets.append(header_label_col)
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
        machines = app.maas.client.get_machines()
        if machines is None:
            if not self.loading:
                self.loading = True
                p = (Text("\n\nLoading...", align='center'),
                     self.machine_pile.options())
                self.machine_pile.contents.append(p)
            return
        if self.loading:
            self.loading = False
            self.machine_pile.contents = self.machine_pile.contents[:-1]

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

            filter_label = m.filter_label()
            if self.filter_string != "" and \
               self.filter_string not in filter_label:
                self.remove_machine(m)
                continue

            mw = self.find_machine_widget(m)
            if mw is None:
                mw = self.add_machine_widget(m)
            mw.all_assigned = self.all_assigned
            mw.update()

        self.filter_edit_box.set_info(len(self.machine_widgets),
                                      n_satisfying_machines)

        self.sort_machine_widgets()

    def add_machine_widget(self, machine):
        mw = MachineWidget(machine,
                           self.application,
                           self.select_cb,
                           self.unselect_cb,
                           self.controller,
                           self.show_assignments)
        self.machine_widgets.append(mw)
        options = self.machine_pile.options()
        self.machine_pile.contents.append((mw, options))

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
            if not isinstance(mw, MachineWidget):
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
