""" Step widget, attaches properties from steps to urwid Text widgets
"""

from urwid import Text
from ubuntui.widgets.input import (StringEditor, YesNo,
                                   PasswordEditor, IntegerEditor)


class StepWidget:
    INPUT_TYPES = {
        'text': StringEditor(),
        'password': PasswordEditor(),
        'boolean': YesNo(),
        'integer': IntegerEditor()
    }

    def __init__(self, step_model):
        self.step_model = step_model
        self.title = Text(self.step_model.title)
        self.description = Text(self.step_model.description)
        self.result = Text('')
        self.icon = Text(("pending_icon", "\N{HOURGLASS}"))
        self.viewable = self.step_model.viewable
        self.path = self.step_model.path

        self.additional_input = []
        if len(self.step_model.additional_input) > 0:
            for i in self.step_model.additional_input:
                widget = {
                    "label": Text(i['label']),
                    "key": i['key'],
                    "input": self.INPUT_TYPES.get(i['type'])
                }
                if 'default' in i:
                    widget['input'] = StringEditor(default=i['default'])

                self.additional_input.append(widget)
