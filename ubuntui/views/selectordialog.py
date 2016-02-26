from collections import OrderedDict
from urwid import (WidgetWrap, signals, emit_signal, connect_signal,
                   RadioButton, Button, Columns, Text, Pile,
                   Divider, Filler)
from ubuntui.utils import Color, Padding


class SelectorWidget(WidgetWrap):

    """
    Simple selector box
    """
    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, title, opts, cb):
        """ Init

        Arguments:
        title: Title of widget
        opts: List of string options
        cb: callback function
        """
        self.title = title
        self.radio_items = OrderedDict()
        for item in opts:
            self.add_radio(item)
        connect_signal(self, 'done', cb)
        super().__init__(self._build_widget())

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
        self.emit_done_signal(selected_item)

    def cancel(self, button):
        raise SystemExit("Installation cancelled.")

    def emit_done_signal(self, *args):
        emit_signal(self, 'done', *args)


class SelectorWithDescriptionWidget(WidgetWrap):

    """
    Simple selector box

    :param str title: title of selections
    :param list opts: items to select ('name', 'description')
    :param cb: callback
    :returns: item selected from dialog
    """
    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, title, opts, cb):
        self.title = title
        self.radio_items = OrderedDict()
        for item, desc in opts:
            self.add_radio(item, desc)
        connect_signal(self, 'done', cb)
        super().__init__(self._build_widget())

    def add_radio(self, item, desc, group=[]):
        self.radio_items[item] = (RadioButton(group, item), desc)

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
            opt, desc = self.radio_items[item]
            col = Columns(
                [
                    ("weight", 0.4, opt),
                    Text(desc)
                ], dividechars=1)
            total_items.append(Padding.center_60(col))
        total_items.append(
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)))
        total_items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(total_items), valign='middle')

    def submit(self, button):
        for item in self.radio_items.keys():
            _item = self.radio_items[item][0]
            if _item.get_state():
                selected_item = _item.label
        self.emit_done_signal(selected_item)

    def cancel(self, button):
        raise SystemExit("Installation cancelled.")

    def emit_done_signal(self, *args):
        emit_signal(self, 'done', *args)
