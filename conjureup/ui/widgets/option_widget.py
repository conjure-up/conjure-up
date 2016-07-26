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
from urwid import (CheckBox, Columns, connect_signal, GridFlow,
                   IntEdit, Pile, Text, WidgetWrap)
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.input import StringEditor
from ubuntui.utils import Color, Padding
import logging

log = logging.getLogger('conjure')


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
        desc_text = Text(["\n", strip_solo_dots(self.description)])

        self.reset_button = PlainButton("Reset to Default", self.do_reset)
        if self.optype == OptionType.BOOLEAN:
            self.control = CheckBox('', state=bool(self.current_value))
            self.wrapped_control = self.control
        elif self.optype == OptionType.INT:
            self.control = IntEdit(default=self.current_value)
            self.wrapped_control = Color.string_input(
                self.control, focus_map='string_input focus')
        elif self.optype == OptionType.STRING:
            edit_text = self.current_value or ""
            self.control = StringEditor(edit_text=edit_text)
            self.wrapped_control = Color.string_input(
                self.control, focus_map='string_input focus')
        else:
            raise Exception("Unknown option type")

        self.control_columns = Columns(
            [
                ('pack', Text("{}:".format(self.name), align='right')),
                (80, self.wrapped_control)
            ],
            dividechars=1
        )

        if self.optype == OptionType.STRING:
            connect_signal(self.control._edit, 'change',
                           self.handle_value_changed)
        else:
            connect_signal(self.control, 'change',
                           self.handle_value_changed)

        button_grid = GridFlow([
            Color.button_secondary(self.reset_button,
                                   focus_map='button_secondary focus')],
                               36, 1, 0, 'right')

        return Pile([Padding.line_break(""),
                     Padding.left(self.control_columns, left=1),
                     Padding.left(desc_text, left=2),
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
