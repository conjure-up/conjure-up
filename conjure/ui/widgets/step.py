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

    def __init__(self, step):
        self.step = step
        self.title = Text(self.step.get('title', 'No title found'))
        self.description = Text(self.step.get(
            'description', 'No description found'))
        self.result = Text('')
        self.icon = Text(("pending_icon", "\N{HOURGLASS}"))
        self.viewable = step.get('viewable', None)
        self.path = step.get('path', None)

        self.additional_input = []
        if 'additional-input' in self.step \
           and len(self.step['additional-input']) > 0:
            for i in self.step['additional-input']:
                widget = {
                    "label": Text(i['label']),
                    "key": i['key'],
                    "input": self.INPUT_TYPES.get(i['type'])
                }
                if 'default' in i:
                    widget['input'] = StringEditor(default=i['default'])

                self.additional_input.append(widget)
