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

from __future__ import unicode_literals
from urwid import WidgetWrap, Text, Pile, ListBox, BoxAdapter, Divider, Columns
from ubuntui.widgets.buttons import (cancel_btn, menu_btn)
from ubuntui.utils import Color, Padding
from ubuntui.ev import EventLoop
from ubuntui.lists import SimpleList


class WelcomeView(WidgetWrap):
    def __init__(self, common, cb):
        self.common = common
        self.cb = cb
        _pile = [
            Padding.center_90(Text("Choose a solution to get started:")),
            Padding.center_90(Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}")),
            Padding.center_90(self.build_menuable_items()),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(ListBox(_pile))

    def buttons(self):
        cancel = cancel_btn(on_press=self.cancel)

        buttons = [
            Color.button_secondary(cancel, focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def build_menuable_items(self):
        """ Builds a list of bundles available to install
        """
        bundles = self.common['config']['bundles']
        cols = []
        for idx, bundle in enumerate(bundles, 1):
            cols.append(
                Columns(
                    [
                        ("weight", 0.2, Color.body(
                            menu_btn(label="{}. {}".format(idx,
                                                           bundle['name']),
                                     on_press=self.done),
                            focus_map="button_primary focus")),
                        ("weight", 0.3, Text(bundle['summary'],
                                             align="left"))
                    ],
                    dividechars=1
                )
            )
            cols.append(Padding.line_break(""))
        return BoxAdapter(SimpleList(cols),
                          height=len(cols)+2)

    def cancel(self, button):
        EventLoop.exit(0)

    def done(self, result):
        self.cb("Finished.")
