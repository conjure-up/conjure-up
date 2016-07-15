from ubuntui.widgets.input import (StringEditor, YesNo,
                                   PasswordEditor, IntegerEditor)
from urwid import (Text)


class StepModelWidget:
    INPUT_TYPES = {
        'text': StringEditor(),
        'password': PasswordEditor(),
        'boolean': YesNo(),
        'integer': IntegerEditor()
    }

    def __init__(self, step_model):
        """

        Arguments:
        step_model: step model
        cb: submit button cb
        """
        self.title = Text(('info_minor', step_model.title))
        self.description = Text(('info_minor', step_model.description))
        self.result = Text(step_model.result)
        self.icon = Text(("pending_icon", "\N{BALLOT BOX}"))

        self.additional_input = []
        if len(step_model.additional_input) > 0:
            for i in step_model.additional_input:
                widget = {
                    "label": Text(('info_minor', i['label'])),
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

        def __repr__(self):
            return "<Additional Input: {}".format(self.additional_input)
