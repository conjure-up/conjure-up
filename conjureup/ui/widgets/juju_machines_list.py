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
# along with this program.  If not, see <http://www.gnu.org/licenses>.

import logging
from operator import attrgetter

from urwid import AttrMap, Columns, Divider, Pile, Text, WidgetWrap

from conjureup.ui.widgets.filter_box import FilterBox
from conjureup.ui.widgets.juju_machine_widget import JujuMachineWidget
from ubuntui.widgets.buttons import PlainButton

log = logging.getLogger('bundleplacer')


class JujuMachinesList(WidgetWrap):

    """A list of machines in a juju bundle, with configurable action
    buttons for each machine.

    application - an application

    machines - list of machine info dicts

    assign_cb - a function that takes a machine and assignmenttype to
    perform the button action

    unassign_cb - a function that takes a machine and clears assignments

    controller - a controller object that provides get_placements and get_pin.

    show_constraints - bool, whether or not to show the constraints
    for each of the machines

    title_widgets - A list of widgets to be used in place of the default
    title.

    show_assignments - bool, whether or not to show the assignments
    for each of the machines.

    show_filter_box - bool, show text box to filter listed machines

    """

    def __init__(self, application, machines, assign_cb, unassign_cb,
                 add_machine_cb, remove_machine_cb,
                 controller,
                 show_constraints=True,
                 title_widgets=None, show_assignments=True,
                 show_filter_box=False,
                 show_pins=False):
        self.application = application
        self.machines = machines
        self.assign_cb = assign_cb
        self.unassign_cb = unassign_cb
        self.add_machine_cb = add_machine_cb
        self.remove_machine_cb = remove_machine_cb
        self.controller = controller
        self.machine_widgets = []
        self.show_assignments = show_assignments
        self.all_assigned = False
        self.show_filter_box = show_filter_box
        self.show_pins = show_pins
        self.filter_string = ""
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
            title_widgets = [Text("Machines", align='center')]

        self.filter_edit_box = FilterBox(self.handle_filter_change)

        header_widgets = title_widgets + [Divider()]

        if self.show_filter_box:
            header_widgets += [self.filter_edit_box, Divider()]
        labels = ["ID", "Cores", "Memory (GiB)", "Storage (GiB)"]
        if self.show_assignments:
            labels += ["Assignments", ""]
        else:
            labels += [""]

        header_label_col = Columns([Text(m) for m in labels],
                                   dividechars=2)
        header_widgets.append(header_label_col)
        self.header_padding = len(header_widgets)
        self.add_new_button = AttrMap(
            PlainButton("Add New Machine",
                        on_press=self.do_add_machine),
            'button_secondary',
            'button_secondary focus')

        self.machine_pile = Pile(header_widgets + self.machine_widgets +
                                 [self.add_new_button])
        return self.machine_pile

    def do_add_machine(self, sender):
        self.add_machine_cb()
        self.update()

    def remove_machine(self, sender):
        self.remove_machine_cb()
        self.update()

    def handle_filter_change(self, edit_button, userdata):
        self.filter_string = userdata
        self.update()

    def find_machine_widget(self, midx):
        return next((mw for mw in self.machine_widgets if
                     mw.juju_machine_id == midx), None)

    def update(self):

        for midx, md in sorted(self.machines.items()):
            allvalues = ["{}={}".format(k, v) for k, v in md.items()]
            filter_label = midx + " " + " ".join(allvalues)
            if self.filter_string != "" and \
               self.filter_string not in filter_label:
                self.remove_machine_widget(midx)
                continue

            mw = self.find_machine_widget(midx)
            if mw is None:
                mw = self.add_machine_widget(midx, md)
            mw.all_assigned = self.all_assigned
            mw.update()

        n = len(self.machine_widgets)
        self.filter_edit_box.set_info(n, n)

        self.sort_machine_widgets()

    def add_machine_widget(self, midx, md):
        mw = JujuMachineWidget(midx, md,
                               self.application,
                               self.assign_cb,
                               self.unassign_cb,
                               self.controller,
                               self.show_assignments,
                               self.show_pins)
        self.machine_widgets.append(mw)
        options = self.machine_pile.options()
        self.machine_pile.contents.insert(
            len(self.machine_pile.contents) - 1,
            (mw, options))

        return mw

    def remove_machine_widget(self, midx):
        mw = self.find_machine_widget(midx)
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

        self.machine_widgets.sort(key=attrgetter('juju_machine_id'))

        def wrappedkeyfunc(t):
            mw, options = t
            if isinstance(mw, JujuMachineWidget):
                return "B{}".format(mw.juju_machine_id)
            if mw in [self.add_new_button]:
                return 'C'
            return 'A'

        self.machine_pile.contents.sort(key=wrappedkeyfunc)

    def focus_prev_or_top(self):
        self.update()
        try:
            if self.machine_pile.focus_position <= self.header_padding:
                self.machine_pile.focus_position = self.header_padding
        except IndexError:
            log.debug("index error in machines_list focus_top")
