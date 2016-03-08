from urwid import (WidgetWrap, RadioButton, Button, Columns, Text, Pile,
                   Divider, Filler)
from ubuntui.utils import Color, Padding
from ubuntui.ev import EventLoop
from collections import OrderedDict


class CloudView(WidgetWrap):
    def __init__(self, common, clouds, cb):
        self.common = common
        self.cb = cb
        self.config = self.common['config']
        self.title = "Clouds"
        self.radio_items = OrderedDict()
        for item in clouds:
            self.add_radio(item)
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

    def add_radio(self, item, group=[]):
        self.radio_items[item] = RadioButton(group, item)

    def _build_buttons(self):
        buttons = [
            Color.button_primary(
                Button("Confirm", self.submit),
                focus_map='button_primary focus'),
            Color.button_secondary(
                Button("Cancel", self.cancel),
                focus_map='button_secondary focus')
        ]
        return Pile(buttons)

    def _build_widget(self):
        total_items = [
            Padding.center_60(Text(self.title, align="center")),
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1))
        ]
        for item in self.radio_items.keys():
            opt = self.radio_items[item]
            col = Columns([opt])
            total_items.append(Padding.center_60(col))
        total_items.append(Padding.line_break(""))
        total_items.append(
            Padding.center_60(
                Color.button_primary(
                    Button("Add a new cloud", self.submit_new_cloud),
                    focus_map='button_primary focus'
                )
            )
        )
        total_items.append(
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)))
        total_items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(total_items), valign='middle')

    def submit(self, button):
        for item in self.radio_items.keys():
            _item = self.radio_items[item]
            if _item.get_state():
                selected_item = _item.label
        self.cb(selected_item)

    def submit_new_cloud(self, button):
        self.cb(None, create_cloud=True)

    def cancel(self, btn):
        EventLoop.exit(0)
