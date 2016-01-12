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

from urwid import WidgetWrap, Text, Filler, Pile
from ubuntui.utils import Padding, Color
from ubuntui.widgets.buttons import (cancel_btn)


class FinishView(WidgetWrap):
    def __init__(self, common, cb):
        self.common = common
        self.cb = cb
        self.text = Text("Installing bundle...")
        _pile = [
            Padding.center_79(self.text),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="middle"))

    def buttons(self):
        cancel = cancel_btn(label="Quit", on_press=self.cancel)

        buttons = [
            Color.button_secondary(cancel, focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def set_status(self, msg):
        current = self.text.get_text()[0]
        self.text.set_text("{}\n{}".format(current, msg))

    def cancel(self, btn):
        self.cb()
