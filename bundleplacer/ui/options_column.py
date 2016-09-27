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

import logging
from enum import Enum

from urwid import (
    CheckBox,
    Divider,
    GridFlow,
    IntEdit,
    Pile,
    Text,
    WidgetWrap,
    connect_signal
)

from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.input import StringEditor

log = logging.getLogger('bundleplacer')


class OptionType(Enum):
    BOOLEAN = 0
    STRING = 1
    INT = 2


def strip_solo_dots(s):
    ls = s.split("\n")
    rl = []
    for l in ls:
        if l == ".":
            rl.append("")
        else:
            rl.append(l)
    return "\n".join(rl)


class OptionWidget(WidgetWrap):

    def __init__(self, name, optype, description, default,
                 current_value=None, value_changed_callback=None):
        self.name = name
        self.optype = OptionType.__members__[optype.upper()]
        self.description = description
        self.default = default
        self.current_value = current_value or default
        w = self.build_widgets()
        self.value_changed_callback = value_changed_callback
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def build_widgets(self):
        title_text = Text([("body", self.name)],
                          align="center")

        desc_text = Text(["\n", strip_solo_dots(self.description)])

        self.reset_button = PlainButton("Reset to Default", self.do_reset)
        if self.optype == OptionType.BOOLEAN:
            self.control = CheckBox(self.name, state=bool(self.current_value))

        elif self.optype == OptionType.INT:
            self.control = IntEdit(caption="{}: ".format(self.name),
                                   default=self.current_value)
        elif self.optype == OptionType.STRING:
            edit_text = self.current_value or ""
            self.control = StringEditor(
                caption="{}: ".format(self.name),
                edit_text=edit_text)
        else:
            raise Exception("Unknown option type")

        if self.optype == OptionType.STRING:
            connect_signal(self.control._edit, 'change',
                           self.handle_value_changed)
        else:
            connect_signal(self.control, 'change',
                           self.handle_value_changed)

        button_grid = GridFlow([self.reset_button],
                               36, 1, 0, 'right')

        return Pile([Divider(), title_text, desc_text, self.control,
                     button_grid])

    def handle_value_changed(self, sender, value):
        self.current_value = value
        if self.optype == OptionType.INT:
            v = value
            if value not in ['', '-']:
                v = int(value)
            self.value_changed_callback(self.name, v)
        else:
            self.value_changed_callback(self.name, self.current_value)

    def do_reset(self, sender):
        self.current_value = str(self.default)
        if self.optype == OptionType.BOOLEAN:
            newstate = True if self.current_value == "True" else False
            self.control.state = newstate
        elif self.optype == OptionType.INT:
            edit_text = self.current_value or ""
            self.control.set_edit_text(edit_text)
        elif self.optype == OptionType.STRING:
            edit_text = self.current_value or ""
            self.control.value = edit_text

    def update(self):
        pass


class OptionsColumn(WidgetWrap):

    """UI to edit options of a service
    """

    def __init__(self, display_controller, placement_controller,
                 placement_view, metadata_controller):
        self.placement_controller = placement_controller
        self.metadata_controller = metadata_controller
        self.service = None
        self.filter_string = ""
        self.placement_view = placement_view

        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def build_widgets(self):
        self.title = Text('')
        self.option_widgets = []
        self.pile = Pile([Divider(), self.title] + self.option_widgets)
        return self.pile

    def refresh(self):
        self.set_service(self.service)

    def set_service(self, service):
        self.service = service
        self.metadata_controller.add_charm(service.csid.as_str_without_rev())
        self.pile.contents = self.pile.contents[:2]
        self.option_widgets = []

    def update(self):
        if self.service is None:
            return

        self.title.set_text(('body', "Edit Options for {}".format(
            self.service.service_name)))

        if len(self.option_widgets) == 0:
            if self.filter_string != "":
                self.title.set_text(
                    ('body',
                     "No options match '{}'".format(self.filter_string)))
            else:
                self.title.set_text(('body', "Loading Options..."))
        else:
            self.title.set_text(('body', "Edit Options: (Changes are "
                                 "saved immediately)"))

        mc = self.metadata_controller
        options = mc.get_options(self.service.csid.as_str_without_rev())

        for opname, opdict in sorted(options.items()):
            if self.filter_string != "" and \
               self.filter_string not in opname:
                self.remove_option_widget(opname)
                continue
            ow = self.find_option_widget(opname)
            if ow is None:
                ow = self.add_option_widget(opname, opdict)
            ow.update()

        # MMCC TODO set filterbox.set_info

        for w, _ in self.pile.contents[2:]:
            w.update()
        self.sort_option_widgets()

    def handle_filter_change(self, edit_button, userdata):
        self.filter_string = userdata
        self.update()

    def handle_edit(self, opname, value):
        self.placement_controller.set_option(self.service.service_name,
                                             opname, value)

    def find_option_widget(self, opname):
        return next((ow for ow in self.option_widgets if
                     ow.name == opname), None)

    def add_option_widget(self, opname, opdict):
        cv = self.service.options.get(opname, None)
        ow = OptionWidget(opname,
                          opdict['Type'],
                          opdict['Description'],
                          opdict['Default'],
                          current_value=cv,
                          value_changed_callback=self.handle_edit)

        self.option_widgets.append(ow)
        self.pile.contents.append((ow,
                                   self.pile.options()))
        return ow

    def remove_option_widget(self, opname):
        ow = self.find_option_widget(opname)
        if ow is None:
            return

        self.option_widgets.remove(ow)
        ow_idx = 0
        for w, opts in self.pile.contents:
            if w == ow:
                break
            ow_idx += 1

        c = self.pile.contents[:ow_idx] + \
            self.pile.contents[ow_idx + 1:]
        self.pile.contents = c

    def focus_prev_or_top(self):
        # ? self.pile.focus_position = len(self.pile.contents) - 1

        if len(self.pile.contents) <= 2:
            return
        pos = self.pile.focus_position
        if pos < 2:
            self.pile.focus_position = 2

    def sort_option_widgets(self):
        def keyfunc(ow):
            return str(ow.name)
        self.option_widgets.sort(key=keyfunc)

        def wrappedkeyfunc(t):
            rw, options = t
            if isinstance(rw, OptionWidget):
                return keyfunc(rw)
            return 'A'

        self.pile.contents.sort(key=wrappedkeyfunc)
