from urwid import WidgetWrap, Text, Filler, Pile
from ubuntui.utils import Padding, Color
from ubuntui.widgets.buttons import (cancel_btn)
from ubuntui.ev import EventLoop


class DeployView(WidgetWrap):
    def __init__(self, app, cb):
        self.app = app
        self.text = Text("deploying...")
        _pile = [
            Padding.center_79(self.text),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="middle"))

    def buttons(self):
        cancel = cancel_btn(on_press=self.cancel)

        buttons = [
            Color.button_secondary(cancel, focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def set_status(self, msg):
        self.text.set_text(msg)

    def cancel(self, btn):
        EventLoop.exit(0)
