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


from urwid import (AttrMap, Divider, GridFlow, Pile, WidgetWrap,
                   Padding, Text)

from ubuntui.widgets.buttons import MenuSelectButton


class ServiceWidgetState(Enum):
    CHOOSING = 0
    SELECTED = 1
    UNSELECTED = 2


class SimpleServiceWidget(WidgetWrap):

    """A widget displaying a service as a button

    charm_class - the class describing the service to display

    placement_controller - a PlacementController instance

    display_controller - a PlacerView instance

    callback - a function to be called when either of the buttons is
    pressed. The service will be passed to the function as userdata.

    show_placements - display the machine(s) currently assigned to
    host this service, both planned deployments (aka 'assignments',
    and already-deployed, called 'deployments').

    """

    def __init__(self, charm_class, placement_controller,
                 display_controller, show_placements=False):
        self.charm_class = charm_class
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
        self.title_markup = [self.charm_class.display_name]

        if self.charm_class.subordinate:
            self.button = MenuSelectButton("I AM A SUBORDINATE SERVICE")
        else:
            self.button = MenuSelectButton("I AM A SERVICE", self.do_select)

        self.action_button_grid = GridFlow([], 22, 1, 1, 'right')
        self.action_buttons = []

        self.pile = Pile([self.button])
        return self.pile

    def get_markup(self):
        if self.charm_class.subordinate:
            return self.title_markup, []

        if self.state == ServiceWidgetState.SELECTED:
            selection_markup = ["\N{BALLOT BOX WITH CHECK} "]
        else:
            selection_markup = ["\N{BALLOT BOX} "]

        main_markup = selection_markup + self.title_markup

        info_markup = []
        p = self.placement_controller.get_assignments(self.charm_class)
        nr = self.charm_class.required_num_units()
        info_str = " ({} of {} placed)".format(len(p), nr)

        info_markup.append(info_str)

        def string_for_placement_dict(d):
            s = []
            for atype, ml in d.items():
                n = len(ml)
                s.append("    {} ({}): ".format(atype.name, n))
                if len(ml) == 0:
                    s.append("\N{DOTTED CIRCLE}")
                else:
                    s.append(", ".join([m.hostname for m in ml]))
            if len(s) == 0:
                return ["None"]
            return s

        info_markup += ["    Assignments: "]
        ad = self.placement_controller.get_assignments(self.charm_class)
        info_markup += string_for_placement_dict(ad)
        return main_markup, info_markup

    def update_choosing(self):
        title_markup, _ = self.get_markup()
        msg = Padding(Text(title_markup), left=2, right=2, align='center')
        self.pile.contents = [(msg, self.pile.options()),
                              (self.action_button_grid,
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
        self.update_action_buttons()

        if self.state == ServiceWidgetState.CHOOSING:
            self.update_choosing()
        else:
            self.update_default()

    def update_action_buttons(self):

        all_actions = [('Choose Placement',
                        self.handle_placement_button_pressed),
                       ('Edit Relations',
                        self.handle_relation_button_pressed)]

        self.action_buttons = [AttrMap(MenuSelectButton(label, on_press=func),
                                       'button_secondary',
                                       'button_secondary focus')
                               for label, func in all_actions]

        self.action_buttons.append(AttrMap(
            MenuSelectButton("Cancel",
                             on_press=self.do_cancel),
            'button_secondary',
            'button_secondary focus'))

        opts = self.action_button_grid.options()
        self.action_button_grid.contents = [(b, opts) for b in
                                            self.action_buttons]

    def do_select(self, sender):
        self.display_controller.clear_selections()
        if self.state == ServiceWidgetState.SELECTED:
            self.state = ServiceWidgetState.UNSELECTED
            self.display_controller.set_selected_charm(None)
        else:
            self.display_controller.set_selected_charm(self.charm_class)
            self.state = ServiceWidgetState.CHOOSING
            self.pile.focus_position = 1
            self.action_button_grid.focus_position = 0
        self.update()

    def do_cancel(self, sender):
        self.state = ServiceWidgetState.UNSELECTED
        self.update()
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
