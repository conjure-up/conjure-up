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

from urwid import WidgetWrap, Text, Pile, Columns, ListBox
from ubuntui.widgets.buttons import (cancel_btn, done_btn)
from ubuntui.widgets.meta import MetaScroll
from ubuntui.utils import Color, Padding
from ubuntui.ev import EventLoop


class WelcomeView(WidgetWrap):
    def __init__(self, common, cb):
        self.common = common
        self.cb = cb
        _pile = [
            Padding.center_79(self.build_menuable_items()),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(ListBox(_pile))

    def buttons(self):
        cancel = cancel_btn(on_press=self.cancel)
        done = done_btn(on_press=self.done)

        buttons = [
            Color.button_primary(done, focus_map='button_primary focus'),
            Color.button_secondary(cancel, focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def build_menuable_items(self):
        """ Builds a list of bundles available to install
        """
        items = [Text(x) for x in self.common['config']['bundles']]
        return Pile(items)

    # def build_config_items(self):
    #     """ Builds the form for modifying the charms config options
    #     """
    #     self._generate_config_options()
    #     items = [MetaScroll()]
    #     cols = []
    #     for k, v in self.charm_config_ui.items():
    #         cols.append(
    #             Columns(
    #                 [
    #                     ("weight", 0.2, Text(k, align="right"))
    #                     ("weight", 0.3, Pile([
    #                         v['input'],
    #                         v['description']
    #                     ]))
    #                 ]
    #             )
    #         )
    #     items.expand(cols)
    #     return items

    def cancel(self, button):
        EventLoop.exit(0)

    def done(self, result):
        self.cb("Finished.")
