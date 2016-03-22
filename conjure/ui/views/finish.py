from urwid import WidgetWrap, Text, Filler, Pile
from ubuntui.utils import Padding, Color
from ubuntui.widgets.buttons import (cancel_btn)


class FinishView(WidgetWrap):
    def __init__(self, app, cb):
        self.app = app
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
