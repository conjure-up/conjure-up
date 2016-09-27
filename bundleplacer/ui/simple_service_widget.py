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

from enum import Enum

from urwid import AttrMap, Columns, Divider, Padding, Pile, Text, WidgetWrap

from bundleplacer.assignmenttype import AssignmentType
from ubuntui.widgets.buttons import MenuSelectButton, PlainButton


class ServiceWidgetState(Enum):
    CHOOSING = 0
    SELECTED = 1
    UNSELECTED = 2


class SimpleServiceWidget(WidgetWrap):

    """A widget displaying a service as a button

    service - the service to display

    placement_controller - a PlacementController instance

    display_controller - a PlacerView instance

    callback - a function to be called when either of the buttons is
    pressed. The service will be passed to the function as userdata.

    show_placements - display the machine(s) currently assigned to
    host this service, both planned deployments (aka 'assignments',
    and already-deployed, called 'deployments').

    """

    def __init__(self, service, placement_controller,
                 display_controller, show_placements=False):
        self.service = service
        self.placement_controller = placement_controller
        self.display_controller = display_controller
        self.show_placements = show_placements
        self.state = ServiceWidgetState.UNSELECTED
        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def build_widgets(self):

        self.button = MenuSelectButton("I AM A SERVICE", self.do_select)

        self.action_button_cols = Columns([], dividechars=1)
        self.action_buttons = []

        self.pile = Pile([self.button])
        return self.pile

    def get_markup(self):
        if self.service.subordinate:
            return [self.service.service_name +
                    " (subordinate)\n  " +
                    self.service.charm_source], []

        nr = self.service.required_num_units()
        pl = "s" if nr > 1 else ""
        title_markup = [self.service.service_name +
                        "\n  {} unit{}: ".format(nr, pl) +
                        self.service.charm_source]
        info_markup = []

        if not self.display_controller.has_maas:
            return title_markup, info_markup

        pd = self.placement_controller.get_assignments(self.service)
        nplaced = sum([len(pd[k]) for k in pd])

        if nr - nplaced > 0:
            pl = ""
            if nr - nplaced > 1:
                pl = "s"
            info_str = ("  {} unit{} will be auto-placed "
                        "by Juju\n".format(nr - nplaced, pl))

            info_markup.append(info_str)

        def string_for_placement_dict(d):
            if self.display_controller.has_maas:
                defstring = "Bare Metal (Default)"
            else:
                defstring = "LXD (Default)"
            s = []
            for atype, ml in sorted(d.items()):
                if atype == AssignmentType.DEFAULT:
                    aname = defstring
                else:
                    aname = atype.name

                hostnames = [m.hostname for m in ml]
                s.append("    {}: {}".format(aname,
                                             ", ".join(hostnames)))
            if len(s) == 0:
                return []
            return "\n".join(s)

        ad = self.placement_controller.get_assignments(self.service)
        info_markup += string_for_placement_dict(ad)
        return title_markup, info_markup

    def update_choosing(self):
        title_markup, _ = self.get_markup()
        msg = Padding(Text(title_markup), left=2, right=2, align='center')
        self.pile.contents = [(msg, self.pile.options()),
                              (self.action_button_cols,
                               self.pile.options()),
                              (Divider(), self.pile.options())]

    def update_default(self):
        title_markup, info_markup = self.get_markup()
        self.button.set_label(title_markup + ["\n"] + info_markup)
        if self.state == ServiceWidgetState.SELECTED:
            b = AttrMap(self.button, 'deploy_highlight_start',
                        'button_secondary focus')
        else:
            b = AttrMap(self.button, 'text', 'button_secondary focus')

        self.pile.contents = [(b, self.pile.options()),
                              (Divider(), self.pile.options())]

    def update(self):
        self.service = next((s for s in
                             self.placement_controller.bundle.services
                             if s.service_name == self.service.service_name),
                            self.service)
        self.update_action_buttons()

        if self.state == ServiceWidgetState.CHOOSING:
            self.update_choosing()
        else:
            self.update_default()

    def keypress(self, size, key):
        if key == 'backspace':
            self.display_controller.remove_service(self.service)
        elif key == '+':
            if not self.service.subordinate:
                self.display_controller.scale_service(self.service, 1)
        elif key == '-':
            if not self.service.subordinate:
                self.display_controller.scale_service(self.service, -1)

        return super().keypress(size, key)

    def update_action_buttons(self):
        all_actions = []
        if self.display_controller.has_maas:
            all_actions = [('Choose Placement',
                            self.handle_placement_button_pressed)]
        all_actions += [('Edit Relations',
                         self.handle_relation_button_pressed),
                        ('Edit Options',
                         self.handle_options_button_pressed)]

        self.action_buttons = [AttrMap(PlainButton(label, on_press=func),
                                       'button_secondary',
                                       'button_secondary focus')
                               for label, func in all_actions]

        self.action_buttons.append(AttrMap(
            PlainButton("Cancel",
                        on_press=self.do_cancel),
            'button_secondary',
            'button_secondary focus'))

        opts = self.action_button_cols.options()
        self.action_button_cols.contents = [(b, opts) for
                                            b in self.action_buttons]

    def do_select(self, sender):
        self.display_controller.clear_selections()
        if self.state == ServiceWidgetState.SELECTED:
            self.state = ServiceWidgetState.UNSELECTED
            self.display_controller.set_selected_service(None)
        else:
            self.display_controller.set_selected_service(self.service)
            self.state = ServiceWidgetState.CHOOSING
            self.pile.focus_position = 1
            self.action_button_cols.focus_position = 0
        self.update()

    def do_cancel(self, sender):
        self.state = ServiceWidgetState.UNSELECTED
        self.update()
        self.display_controller.show_default_view()
        self.pile.focus_position = 0

    def handle_placement_button_pressed(self, sender):
        self.state = ServiceWidgetState.SELECTED
        self.update()
        self.display_controller.edit_placement()
        self.pile.focus_position = 0

    def handle_relation_button_pressed(self, sender):
        self.state = ServiceWidgetState.SELECTED
        self.update()
        self.display_controller.edit_relations()
        self.pile.focus_position = 0

    def handle_options_button_pressed(self, sender):
        self.state = ServiceWidgetState.SELECTED
        self.update()
        self.display_controller.edit_options()
        self.pile.focus_position = 0
