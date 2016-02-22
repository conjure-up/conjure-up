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


from urwid import (AttrMap, Button, GridFlow,
                   Padding, Pile, SelectableIcon, Text, WidgetWrap)

from bundleplacer.utils import format_constraint
from bundleplacer.state import CharmState


class ServiceWidget(WidgetWrap):

    """A widget displaying a service and associated actions.

    charm_class - the class describing the service to display

    controller - a PlacementController instance

    actions - a list of ('label', function) pairs that will be used to
    create buttons for each machine.  The machine will be passed to
    the function as userdata.

    optionally, actions can be a 3-tuple (pred, 'label', function),
    where pred determines whether to add the button. Pred will be
    passed the charm class.

    show_constraints - display the charm's constraints

    show_placements - display the machine(s) currently assigned to
    host this service, both planned deployments (aka 'assignments',
    and already-deployed, called 'deployments').

    """

    def __init__(self, charm_class, controller, actions=None,
                 show_constraints=False, show_placements=False):
        self.charm_class = charm_class
        self.controller = controller
        if actions is None:
            self.actions = []
        else:
            self.actions = actions
        self.show_constraints = show_constraints
        self.show_placements = show_placements
        w = self.build_widgets()
        self.update()
        super().__init__(w)

    def selectable(self):
        return True

    def update_title_markup(self):
        dn = self.charm_class.display_name
        self.title_markup = ["\N{GEAR} {}".format(dn), ""]
        summary = self.charm_class.summary
        if summary != "":
            self.title_markup.append("\n {}\n".format(summary))

    def build_widgets(self):
        self.update_title_markup()
        self.charm_info_widget = Text(self.title_markup)
        self.placements_widget = Text("")

        if self.charm_class.subordinate:
            c_str = [('label', "  (subordinate charm)")]
        elif len(self.charm_class.constraints) == 0:
            c_str = [('label', "  no constraints set")]
        else:
            cpairs = [format_constraint(k, v) for k, v in
                      self.charm_class.constraints.items()]
            c_str = [('label', "  constraints: "), ', '.join(cpairs)]
        self.constraints_widget = Text(c_str)

        self.buttons = []

        self.button_grid = GridFlow(self.buttons, 22, 1, 1, 'right')

        pl = [self.charm_info_widget]

        if self.show_placements:
            pl.append(self.placements_widget)
        if self.show_constraints:
            pl.append(self.constraints_widget)
        pl.append(self.button_grid)

        p = Pile(pl)
        return Padding(p, left=2, right=2)

    def update(self):
        mstr = [""]

        self.update_title_markup()

        state, cons, deps = self.controller.get_charm_state(self.charm_class)

        if state == CharmState.REQUIRED:
            p = self.controller.get_assignments(self.charm_class)
            d = self.controller.get_deployments(self.charm_class)
            nr = self.charm_class.required_num_units()
            info_str = " ({} of {} placed".format(len(p), nr)
            if len(d) > 0:
                info_str += ", {} deployed)".format(len(d))
            else:
                info_str += ")"

            # Add hint to explain why a dep showed up in required
            if len(p) == 0 and len(deps) > 0:
                dep_str = ", ".join([c.display_name for c in deps])
                info_str += " - required by {}".format(dep_str)

            self.title_markup[1] = ('info', info_str)
        elif state == CharmState.CONFLICTED:
            con_str = ", ".join([c.display_name for c in cons])
            self.title_markup[1] = ('error_icon',
                                    ' - Conflicts with {}'.format(con_str))
        elif state == CharmState.OPTIONAL:
            self.title_markup[1] = ""

        def string_for_placement_dict(d):
            s = []
            for atype, ml in d.items():
                n = len(ml)
                s.append(('label', "    {} ({}): ".format(atype.name, n)))
                if len(ml) == 0:
                    s.append("\N{DOTTED CIRCLE}")
                else:
                    s.append(", ".join(["\N{TAPE DRIVE} {}".format(m.hostname)
                                        for m in ml]))
            if len(s) == 0:
                return [('label', "None")]
            return s
        mstr += ["    ", ('label', "Assignments: ")]
        ad = self.controller.get_assignments(self.charm_class)
        dd = self.controller.get_deployments(self.charm_class)
        mstr += string_for_placement_dict(ad)
        mstr += ["\n    ", ('label', "Deployments: ")]
        mstr += string_for_placement_dict(dd)

        self.charm_info_widget.set_text(self.title_markup)
        self.placements_widget.set_text(mstr)

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

            if not predicate(self.charm_class):
                b = AttrMap(SelectableIcon(" (" + label + ")"),
                            'disabled_button', 'disabled_button_focus')
            else:
                b = AttrMap(Button(label, on_press=func,
                                   user_data=self.charm_class),
                            'button_secondary', 'button_secondary focus')
            buttons.append((b, self.button_grid.options()))

        self.button_grid.contents = buttons
