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


from urwid import AttrMap, WidgetWrap, SelectableIcon

from ubuntui.widgets.buttons import MenuSelectButton


class SimpleServiceWidget(WidgetWrap):

    """A widget displaying a service as a button

    charm_class - the class describing the service to display

    controller - a PlacementController instance

    action - a function to be called when the button is pressed. The
    service will be passed to the function as userdata.

    show_placements - display the machine(s) currently assigned to
    host this service, both planned deployments (aka 'assignments',
    and already-deployed, called 'deployments').

    """

    def __init__(self, charm_class, controller, action,
                 show_placements=False):
        self.charm_class = charm_class
        self.controller = controller
        self.action = action
        self.show_placements = show_placements
        self.is_selected = False
        w = self.build_widgets()
        self.update()
        super().__init__(w)

    def selectable(self):
        return True

    def build_widgets(self):
        self.title_markup = [self.charm_class.display_name + "\n"]

        if self.charm_class.subordinate:
            self.button = SelectableIcon("I AM A SUBORDINATE SERVICE")
        else:
            self.button = MenuSelectButton("I AM A SERVICE", self.do_action)

        if self.is_selected:
            return AttrMap(self.button, 'deploy_highlight_start',
                           'button_secondary focus')
        else:
            return AttrMap(self.button, 'text',
                           'button_secondary focus')

    def update(self):
        self._w = self.build_widgets()

        if self.is_selected:
            selection_markup = ["\n\N{BALLOT BOX WITH CHECK} "]
        else:
            selection_markup = ["\n\N{BALLOT BOX} "]

        if self.charm_class.subordinate:
            self.button.set_text([("\n  ")] + self.title_markup)
            return

        markup = selection_markup + self.title_markup

        p = self.controller.get_assignments(self.charm_class)
        nr = self.charm_class.required_num_units()
        info_str = " ({} of {} placed)".format(len(p), nr)

        markup.append(info_str)

        def string_for_placement_dict(d):
            s = []
            for atype, ml in d.items():
                n = len(ml)
                s.append("    {} ({}): ".format(atype.name, n))
                if len(ml) == 0:
                    s.append("\N{DOTTED CIRCLE}")
                else:
                    s.append(", ".join(["\N{TAPE DRIVE} {}".format(m.hostname)
                                        for m in ml]))
            if len(s) == 0:
                return ["None"]
            return s

        markup += ["    Assignments: "]
        ad = self.controller.get_assignments(self.charm_class)
        markup += string_for_placement_dict(ad)

        self.button.set_label(markup)

    def do_action(self, sender):
        self.is_selected = not self.is_selected
        self.update()
        self.action(self)
