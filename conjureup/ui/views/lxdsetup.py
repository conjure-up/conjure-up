from urwid import Filler, Pile, Text, WidgetWrap

from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import cancel_btn, confirm_btn
from ubuntui.widgets.hr import HR
from ubuntui.widgets.text import Instruction


class LXDSetupView(WidgetWrap):

    def __init__(self, app, msg, cb):
        self.app = app
        self.msg = msg
        self.cb = cb
        _pile = [
            Padding.center_60(Instruction(
                "LXD Configuration is required"
            )),
            Padding.center_60(HR()),
            Padding.center_60(self.build_info()),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="middle"))

    def _swap_focus(self):
        if self._w.body.focus_position == 2:
            self._w.body.focus_position = 4
        else:
            self._w.body.focus_position = 2

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

    def buttons(self):
        confirm = confirm_btn(on_press=self.submit)
        cancel = cancel_btn(on_press=self.cancel)

        buttons = [
            Color.button_primary(confirm, focus_map='button_primary focus'),
            Color.button_secondary(cancel, focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def build_info(self):
        items = [
            Text(self.msg)
        ]
        return Pile(items)

    def cancel(self, btn):
        self.cb(back=True)

    def submit(self, result):
        self.cb(needs_lxd_setup=True)
