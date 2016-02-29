from ubuntui.ev import EventLoop
from ubuntui.utils import Color, Padding
from ubuntui.widgets.input import StringEditor
from urwid import (WidgetWrap, RadioButton, Pile, Button,
                   Text, Divider, Filler)
from conjure.api.models import list_models
from conjure.juju import Juju


class JujuControllerView(WidgetWrap):
    def __init__(self, common, models, cb):
        self.common = common
        self.cb = cb
        self.models = models
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
            Padding.center_60(Text("Please select an option below:",
                                   align="center")),
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1))
        ]
        if self.models is not None:
            for k in self.models.keys():
                _models = self.models[k]['accounts']['admin@local']['models']
                items.append(Padding.center_60(Text(k)))
                for m in _models:
                    items.append(Padding.center_60(
                        RadioButton(self.group, "{}:{}".format(k, m))))
                items.append(Padding.line_break(""))
        items.append(
            Padding.center_60(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)))
        items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(items), valign="middle")

    def submit(self, btn):
        # if self.input_new_controller.value is not None:
        #     controller = (self.input_new_controller.value, True)
        # else:
        #     for item in self.group:
        #         if item.get_state():
        #             controller = (item.label, False)
        for item in self.group:
            if item.get_state():
                controller = item.label
        self.cb(controller)

    def cancel(self, btn):
        EventLoop.exit(0)
