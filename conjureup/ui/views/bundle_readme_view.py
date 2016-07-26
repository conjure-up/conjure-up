""" Service Walkthrough view

List out the updated bundle in a cleaner view showing what
charms and their relations will be done.
"""

from glob import glob
import os
from urwid import BoxAdapter, Filler, ListBox, Pile, Text, WidgetWrap

from conjureup import utils
from conjureup.app_config import app
from ubuntui.ev import EventLoop
from ubuntui.widgets.buttons import PlainButton
from ubuntui.widgets.hr import HR
from ubuntui.utils import Color, Padding

import logging

log = logging.getLogger('conjure')


class BundleReadmeView(WidgetWrap):
    def __init__(self, metadata_controller, done_callback, initial_height):
        self.metadata_controller = metadata_controller
        self.done_callback = done_callback
        self.initial_height = initial_height

        w = self.build_widgets()
        super().__init__(w)

        self.pile.focus_position = 1

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key == 'tab':
            cur = self.pile.focus_position
            self.pile.focus_position = 3 if cur == 1 else 1
        else:
            return super(BundleReadmeView, self).keypress(size, key)

    def build_widgets(self):
        readme_files = glob(os.path.join(app.config['spell-dir'], 'README.*'))
        if len(readme_files) == 0:
            self.readme_w = Text("No README found for bundle.")
        else:
            readme_file = readme_files[0]
            if len(readme_files) != 1:
                utils.warning("Unexpected: {} files matching README.*"
                              "- using {}".format(len(readme_files),
                                                  readme_file))
            with open(readme_file) as rf:
                rlines = [Text(l) for l in rf.readlines()]
                self.readme_w = BoxAdapter(ListBox(rlines),
                                           self.initial_height)

        ws = [Text("About {}:".format(app.config['spell'])),
              Padding.right_50(Color.button_primary(
                  PlainButton("Continue",
                              self.do_continue),
                  focus_map='button_primary focus')),
              Padding.center(HR()),
              Padding.center(self.readme_w, left=2),
              Padding.center(HR()),
              Padding.center(Text("Use arrow keys to scroll text "
                                  "and TAB to select the button."))]

        self.pile = Pile(ws)
        return Padding.center_90(Filler(self.pile, valign="top"))

    def handle_readme_updated(self, readme_text_f):
        EventLoop.loop.event_loop._loop.call_soon_threadsafe(
            self._update_readme_on_main_thread,
            readme_text_f)

    def _update_readme_on_main_thread(self, readme_text_f):
        self.readme_w.set_text(readme_text_f.result().splitlines())
        self._invalidate()

    def do_continue(self, arg):
        self.done_callback()
