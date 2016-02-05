# Copyright (c) 2015 Canonical Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from collections import OrderedDict
from urwid import (WidgetWrap, signals, emit_signal, connect_signal,
                   RadioButton, Button, Columns, Text, Pile,
                   Divider, Filler)
from ubuntui.utils import Color, Padding


class SelectorWithDescriptionWidget(WidgetWrap):

    """
    Simple selector box

    :param str title: title of selections
    :param list opts: items to select ('name', 'description')
    :param cb: callback
    :returns: item selected from dialog
    """
    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, title, opts, cb):
        self.title = title
        self.radio_items = OrderedDict()
        for item, desc in opts:
            self.add_radio(item, desc)
        connect_signal(self, 'done', cb)
        super().__init__(self._build_widget())

    def add_radio(self, item, desc, group=[]):
        self.radio_items[item] = (RadioButton(group, item), desc)

    def _build_buttons(self):
        buttons = [
            Color.button_primary(
                Button("Confirm", self.submit),
                focus_map='button_primary focus'),
            Color.button_secondary(
                Button("Cancel", self.cancel),
                focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def _build_widget(self):
        total_items = [
            Padding.center_60(Text(self.title, align="center")),
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1))
        ]
        for item in self.radio_items.keys():
            opt, desc = self.radio_items[item]
            col = Columns(
                [
                    ("weight", 0.4, opt),
                    Text(desc)
                ], dividechars=1)
            total_items.append(Padding.center_60(col))
        total_items.append(
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)))
        total_items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(total_items), valign='middle')

    def submit(self, button):
        for item in self.radio_items.keys():
            _item = self.radio_items[item][0]
            if _item.get_state():
                selected_item = _item.label
        self.emit_done_signal(selected_item)

    def cancel(self, button):
        raise SystemExit("Installation cancelled.")

    def emit_done_signal(self, *args):
        emit_signal(self, 'done', *args)
