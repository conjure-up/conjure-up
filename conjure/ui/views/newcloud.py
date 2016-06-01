from ubuntui.widgets.buttons import (confirm_btn, back_btn)
from ubuntui.widgets.text import Instruction
from ubuntui.utils import Color, Padding
from ubuntui.widgets.hr import HR
from urwid import (WidgetWrap, Pile, Text, Columns, Filler)


class NewCloudView(WidgetWrap):
    def __init__(self, app, cloud, schema, cb):
        self.app = app
        self.cloud = cloud
        self.input_items = schema
        self.cb = cb
        _pile = [
            Padding.center_60(Instruction(
                "Enter your {} credentials:".format(self.cloud.upper()))),
            Padding.center_60(HR()),
            Padding.center_60(self.build_inputs()),
            Padding.line_break(""),
            Padding.center_20(self.buttons())
        ]
        super().__init__(Filler(Pile(_pile), valign="top"))

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
        confirm = confirm_btn(on_press=self.submit, label="Add credential")
        cancel = back_btn(on_press=self.cancel)

        buttons = [
            Color.button_primary(confirm, focus_map='button_primary focus'),
            Color.button_secondary(cancel, focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def build_inputs(self):
        items = []
        for k in self.input_items.keys():
            display = k
            if k.startswith('_'):
                # Don't treat 'private' keys as input
                continue
            if k.startswith('@'):
                # Strip public, not storable attribute
                display = k[1:]
            col = Columns(
                [
                    ('weight', 0.5, Text(display, align='right')),
                    Color.string_input(self.input_items[k],
                                       focus_map='string_input focus')
                ], dividechars=1
            )
            items.append(col)
            items.append(Padding.line_break(""))
        return Pile(items)

    def cancel(self, btn):
        self.cb(back=True)

    def submit(self, result):
        self.cb(self.input_items)
