from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.input import StringEditor
from urwid import (WidgetWrap, RadioButton, Pile, Button,
                   Text, Divider, Filler)
from conjure.api.models import list_models
from conjure.juju import Juju


class JujuControllerView(WidgetWrap):
    def __init__(self, common, controllers, cb):
        self.common = common
        self.cb = cb
        self.controllers = controllers
        self.input_new_controller = StringEditor()
        self.group = []
        self.config = self.common['config']
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

    def _build_widget(self):
        items = [
            Padding.center_60(Text("Controllers", align="center")),
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1))
        ]
        if self.controllers is not None:
            items.append(Padding.center_60(Text("Controller:Model")))
            for c in self.controllers:
                Juju.switch(c)
                items.append(Text(c))
                if len(list_models()) > 0:
                    for m in list_models():
                        items.append(Padding.center_60(
                            RadioButton(self.group, "{}:{}".format(c, m))))
        items.append(Padding.line_break(""))
        items.append(
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)))
        items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(items), valign="middle")

    def submit(self, btn):
        if self.input_new_controller.value is not None:
            controller = (self.input_new_controller.value, True)
        else:
            for item in self.group:
                if item.get_state():
                    controller = (item.label, False)
        self.cb(controller)

    def cancel(self, btn):
        EventLoop.exit(0)
