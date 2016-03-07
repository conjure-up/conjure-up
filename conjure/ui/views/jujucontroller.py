from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.input import StringEditor
from urwid import (WidgetWrap, RadioButton, Pile, Button,
                   Text, Divider, Filler)


class JujuControllerView(WidgetWrap):
    def __init__(self, common, models=None, cb=None):
        self.common = common
        self.cb = cb
        self.models = models
        self.input_new_controller = StringEditor()
        self.group = []
        self.config = self.common['config']

        if self.models is not None:
            super().__init__(self._build_existingcontroller_widget())
        else:
            super().__init__(self._build_newcontroller_widget())

    def _swap_focus(self):
        if self._w.body.focus_position == 3:
            self._w.body.focus_position = 6
        else:
            self._w.body.focus_position = 3

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

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

    def _build_newcontroller_widget(self):
        items = [
            Padding.center_60(Text("Please fill out the input below:",
                                   align="center")),
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)),
            Padding.center_60(self.input_new_controller),
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)),
            Padding.center_20(self._build_buttons())
        ]
        return Filler(Pile(items), valign="middle")

    def _build_existingcontroller_widget(self):
        items = [
            Padding.center_60(Text("Please select an option below:",
                                   align="center")),
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1))
        ]
        if self.models is not None:
            for k in self.models.keys():
                items.append(Padding.center_60(
                    Text("Controller: {}".format(k))))
                for m in self.models[k]:
                    items.append(Padding.center_58(
                        RadioButton(self.group, "{}:{}".format(k, m['name']))))
                items.append(Padding.line_break(""))
        items.append(
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)))
        items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(items), valign="middle")

    def submit(self, btn):
        if self.models is not None:
            for item in self.group:
                if item.get_state():
                    controller = item.label
        else:
            controller = self.input_new_controller.value
        self.cb(controller)

    def cancel(self, btn):
        EventLoop.exit(0)
