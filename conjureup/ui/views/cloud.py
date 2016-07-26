from urwid import (WidgetWrap, Pile,
                   Filler)
from ubuntui.utils import Color, Padding
from ubuntui.widgets.hr import HR
from ubuntui.widgets.text import Instruction
from ubuntui.widgets.buttons import quit_btn, menu_btn
from ubuntui.ev import EventLoop


class CloudView(WidgetWrap):
    def __init__(self, app, clouds, cb):
        self.app = app
        self.cb = cb
        self.clouds = clouds
        self.config = self.app.config
        super().__init__(self._build_widget())

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

    def _swap_focus(self):
        w_count = len(self._w.body.contents) - 1
        if self._w.body.focus_position >= 2 and \
           self._w.body.focus_position < w_count:
            self._w.body.focus_position = w_count
        else:
            self._w.body.focus_position = 2

    def _build_buttons(self):
        cancel = quit_btn(on_press=self.cancel)
        buttons = [
            Padding.line_break(""),
            Color.button_secondary(cancel,
                                   focus_map='button_secondary focus'),
        ]
        return Pile(buttons)

    def _build_widget(self):
        total_items = [
            Padding.center_60(Instruction("Choose a Cloud")),
            Padding.center_60(HR())
        ]
        for item in self.clouds:
            total_items.append(Padding.center_60(
                Color.body(
                    menu_btn(label=item,
                             on_press=self.submit),
                    focus_map='menu_button focus'
                )
            ))

        total_items.append(
            Padding.center_60(HR()))
        total_items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(total_items), valign='top')

    def submit(self, result):
        self.cb(result.label)

    def cancel(self, btn):
        EventLoop.exit(0)
