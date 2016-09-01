from urwid import Columns, Filler, Pile, Text, WidgetWrap

from ubuntui.utils import Color, Padding
from ubuntui.widgets.buttons import back_btn, confirm_btn
from ubuntui.widgets.hr import HR
from ubuntui.widgets.input import StringEditor
from ubuntui.widgets.text import Instruction


class NewCloudView(WidgetWrap):

    def __init__(self, app, cloud, schema, cb):
        self.app = app
        self.cloud = cloud
        self.input_items = schema
        self.cb = cb
        self.confirm_button = Color.button_primary(
            confirm_btn(on_press=self.submit,
                        label="Add credential"),
            focus_map='button_primary focus')
        self.cancel_button = Color.button_secondary(
            back_btn(on_press=self.cancel),
            focus_map='button_secondary focus')

        _pile = [
            Padding.center_60(Instruction(
                "Enter your {} credentials:".format(self.cloud.upper()))),
            Padding.center_60(HR()),
            Padding.center_60(self.build_inputs()),
            Padding.line_break(""),
            Text(""),  # confirm button placeholder
            Padding.center_20(self.cancel_button)
        ]
        self.pile = Pile(_pile)
        super().__init__(Filler(self.pile, valign="top"))
        self.validate()

    def _swap_focus(self):
        if self._w.body.focus_position == 2:
            self._w.body.focus_position = 4
        else:
            self._w.body.focus_position = 2

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        rv = super().keypress(size, key)
        self.validate()
        return rv

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

    def validate(self):
        values = [i.value for i in self.input_items.values()
                  if isinstance(i, StringEditor)]

        if None in values:
            self.pile.contents[-2] = (Padding.center_20(
                Text("Please fill all required fields.")),
                self.pile.options())
        else:
            self.pile.contents[-2] = (Padding.center_20(self.confirm_button),
                                      self.pile.options())

    def cancel(self, btn):
        self.cb(back=True)

    def submit(self, result):
        self.cb(self.input_items)
