from __future__ import unicode_literals
from .widgets.input import (StringEditor, YesNo, Selector, PasswordEditor)
from .utils import Color, Padding
from collections import OrderedDict
from urwid import (Pile, WidgetWrap, Text,
                   Button, Filler, Columns, Divider,
                   signals, emit_signal, connect_signal)

""" re-usable dialog widget """


def opts_to_ui(opts):
    """ Converts option dictionary suitable for input
    """
    converted_opts = []
    for k, v in opts.items():
        caption = k.replace('-', ' ')
        caption = "{} ".format(caption)
        if isinstance(v, bool):
            widget = YesNo()
        elif isinstance(v, list):
            widget = Selector(v)
        elif 'password' in k:
            widget = PasswordEditor()
        else:
            widget = StringEditor()
        converted_opts.append((k, caption, widget))
    return converted_opts


class Dialog(WidgetWrap):

    __metaclass__ = signals.MetaSignals
    signals = ['done']
    # key_conversion_map = {'tab': 'down', 'shift tab': 'up'}

    # List of Tuples in the form of ('key', 'caption', widget)
    input_items = []

    def __init__(self, title, cb):
        self.title = title
        self.cb = cb
        self.input_selection = OrderedDict()
        connect_signal(self, 'done', self.cb)
        super().__init__(self._build_widget())

    def _build_buttons(self):
        buttons = [
            Padding.line_break(""),
            Color.button_primary(
                Button("Confirm", self.submit),
                focus_map='button_primary focus'),
            Color.button_secondary(
                Button("Cancel", self.cancel),
                focus_map='button_secondary focus'),
        ]
        return Pile(buttons)

    def _build_widget(self, **kwargs):
        total_items = [
            Padding.center_60(Text(self.title, align="center")),
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1))
        ]
        if self.input_items:
            for item in self.input_items:
                key, caption, w = item
                self.input_selection[key] = w
                col = Columns(
                    [
                        ("weight", 0.5, Text(caption, align="right")),
                        Color.string_input(self.input_selection[key],
                                           focus_map="string_input focus")
                    ]
                )
                total_items.append(Padding.center_60(col))
        total_items.append(
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)))
        total_items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(total_items), valign='middle')

    def submit(self, button):
        self.emit_done_signal(self.input_selection)

    def cancel(self, button):
        raise SystemExit("Installation cancelled.")

    def emit_done_signal(self, *args):
        emit_signal(self, 'done', *args)
