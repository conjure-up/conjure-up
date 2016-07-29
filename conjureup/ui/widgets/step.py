import json
import os

from ubuntui.utils import Padding, Color
from ubuntui.widgets.hr import HR
from ubuntui.widgets.buttons import submit_btn
from ubuntui.widgets.input import (StringEditor, YesNo,
                                   PasswordEditor, IntegerEditor)

from urwid import (WidgetWrap, Pile, Columns, Text)


class StepWidget(WidgetWrap):
    INPUT_TYPES = {
        'text': StringEditor(),
        'password': PasswordEditor(),
        'boolean': YesNo(),
        'integer': IntegerEditor()
    }

    def __init__(self, app, step_model, cb):
        """
        Arguments:
        step_model: step model
        step_model_widget: step model widget
        cb: callback
        """
        self.app = app
        self.model = step_model

        self.title = Text(('info_minor', step_model.title))
        self.description = Text(('info_minor', step_model.description))
        self.result = Text(step_model.result)
        self.output = Text(('info_minor', ''))
        self.icon = Text(("info_minor", "\N{BALLOT BOX}"))

        self.additional_input = []
        if len(step_model.additional_input) > 0:
            for i in step_model.additional_input:
                widget = {
                    "label": Text(('body', i['label'])),
                    "key": i['key'],
                    "input": self.INPUT_TYPES.get(i['type'])
                }
                if 'default' in i:
                    widget['input'] = StringEditor(default=i['default'])

                self.additional_input.append(widget)
        else:
            widget = {
                "label": Text(""),
                "key": "submit",
                "input": None
            }
            self.additional_input.append(widget)

        self.cb = cb
        self.step_pile = self.build_widget()
        self.show_output = True
        super().__init__(self.step_pile)

    def __repr__(self):
        return "<StepWidget: {}>".format(self.model.title)

    def update(self):
        if not self.show_output:
            return
        if not os.path.exists(self.model.path + ".out"):
            return
        with open(self.model.path + ".out") as outf:
            lines = outf.readlines()
            if len(lines) < 1:
                return
            result = json.loads(lines[-1])
            self.output.set_text(('body', "\n    " +
                                  result['message']))

    def clear_output(self):
        self.output.set_text("")

    def set_description(self, description, color='info_minor'):
        self.description.set_text(
            (color, description))

    def set_icon_state(self, result_code):
        """ updates status icon

        Arguments:
        icon: icon widget
        result_code: 3 types of results, error, waiting, complete
        """
        if result_code == "error":
            self.icon.set_text(
                ("error_icon", "\N{BLACK FLAG}"))
        elif result_code == "waiting":
            self.icon.set_text(
                ("pending_icon", "\N{HOURGLASS}"))
        elif result_code == "active":
            self.icon.set_text(
                ("success_icon", "\N{BALLOT BOX WITH CHECK}"))
        else:
            # NOTE: Should not get here, if we do make sure we account
            # for that error type above.
            self.icon.set_text(("error_icon", "?"))

    @property
    def current_button_index(self):
        """ Returns the pile index where the button is located
        """
        return len(self.step_pile.contents)-2

    @property
    def current_button_widget(self):
        """ Returns the current button widget
        """
        if self.button:
            return self.button

    def clear_button(self):
        """ Clears current button so it can't be pressed again
        """
        self.app.log.debug(
            "Contents: {}".format(
                self.step_pile.contents[self.current_button_index]))
        self.step_pile.contents[self.current_button_index] = (
            Text(""), self.step_pile.options())

    def build_widget(self):
        return Pile([
            Columns(
                [
                    ('fixed', 3, self.icon),
                    self.description,
                ], dividechars=1),
            self.output
        ]
        )

    def generate_additional_input(self):
        """ Generates additional input fields, useful for doing it after
        a previous step is run
        """
        self.set_description(self.model.description, 'body')
        self.icon.set_text((
            'pending_icon',
            self.icon.get_text()[0]
        ))
        for i in self.additional_input:
            self.app.log.debug(i)
            self.step_pile.contents.append((Padding.line_break(""),
                                            self.step_pile.options()))
            column_input = [
                ('weight', 0.5, Padding.left(i['label'], left=5))
            ]
            if i['input']:
                column_input.append(
                    ('weight', 1, Color.string_input(
                        i['input'],
                        focus_map='string_input focus')))
            self.step_pile.contents.append(
                (Columns(column_input, dividechars=3),
                 self.step_pile.options()))

            self.button = submit_btn(on_press=self.submit)
            self.step_pile.contents.append(
                (Padding.right_20(
                    Color.button_primary(self.button,
                                         focus_map='button_primary focus')),
                 self.step_pile.options()))
            self.step_pile.contents.append((HR(), self.step_pile.options()))
        self.step_pile.focus_position = self.current_button_index

    def submit(self, btn):
        self.set_icon_state('waiting')
        self.clear_button()
        self.cb(self.model, self)
