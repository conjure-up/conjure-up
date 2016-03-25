from ubuntui.utils import Color, Padding
from ubuntui.widgets.hr import HR
from ubuntui.widgets.text import Instruction
from ubuntui.widgets.input import StringEditor
from ubuntui.widgets.buttons import (cancel_btn, confirm_btn, PlainButton)
from urwid import (WidgetWrap, Pile,
                   Text, Filler, Columns)


class JujuControllerView(WidgetWrap):
    controller_mode = None

    def __init__(self, app, models=None, cb=None):
        self.app = app
        self.cb = cb
        self.models = models
        self.input_new_controller = StringEditor()
        self.group = []
        self.config = self.app.config

        if self.models is not None:
            self.controller_mode = 'existing'
            super().__init__(self._build_existingcontroller_widget())
        else:
            self.controller_mode = 'new'
            super().__init__(self._build_newcontroller_widget())

    def _swap_focus(self):
        w_count = len(self._w.body.contents) - 1
        pos = self._w.body.focus_position
        if self.controller_mode == 'existing':
            if pos >= 3 and pos < w_count:
                self._w.body.focus_position = w_count
            else:
                self._w.body.focus_position = 3
        else:
            if pos >= 2 and pos < w_count:
                self._w.body.focus_position = w_count
            else:
                self._w.body.focus_position = 2

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

    def _build_buttons(self):
        cancel = cancel_btn(on_press=self.cancel)
        buttons = [
            Padding.line_break(""),
            Color.button_secondary(cancel,
                                   focus_map='button_secondary focus'),
        ]
        return Pile(buttons)

    def _build_newcontroller_widget(self):
        items = [
            Padding.center_60(Instruction("Please fill out the input below:")),
            Padding.center_60(HR()),
            Padding.center_60(
                Columns(
                    [
                        ('weight', 0.2, Text("Model")),
                        Color.string_input(self.input_new_controller,
                                           focus_map='string_input focus'),
                    ]
                )),
            Padding.center_60(HR()),
            Padding.center_20(self._build_buttons())
        ]
        return Filler(Pile(items), valign="middle")

    def _build_existingcontroller_widget(self):
        items = [
            Padding.center_60(
                Instruction(
                    "Please select a model below or optionally "
                    "create a new model:")),
            Padding.center_60(HR())
        ]
        for k in sorted(self.models.keys()):
            controller_name = k.split('local.').pop()

            items.append(Padding.center_60(
                Instruction("Model: {}".format(controller_name))))
            for m in self.models[k]['models']:
                if m['name'] == 'admin':
                    continue
                items.append(
                    Padding.center_50(
                        Color.body(
                            confirm_btn(label="{}:{}".format(controller_name,
                                                             m['name']),
                                        on_press=self.submit),
                            focus_map='menu_button focus'
                        )
                    )
                )
            items.append(Padding.line_break(""))
        items.append(Padding.center_50(
            Color.body(
                PlainButton(label="Select a new Cloud Provider",
                            on_press=self.select_cloud),
                focus_map='menu_button focus')
        ))
        items.append(
            Padding.center_60(HR()))
        items.append(Padding.center_20(self._build_buttons()))
        return Filler(Pile(items), valign="middle")

    def select_cloud(self, btn):
        return self.app.controllers['clouds'].render()

    def submit(self, result):
        self.cb(result.label)

    def cancel(self, btn):
        self.cb(back=True)
