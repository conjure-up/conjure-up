""" Step model
"""


class StepModel:
    def __init__(self, step):
        self.title = step.get('title', '')
        self.description = step.get('description', '')
        self.result = ''
        self.viewable = step.get('viewable', False)
        self.path = step.get('path', None)

        self.additional_input = step.get('additional-input', [])
        self.widget = None

    def __repr__(self):
        return "<t: {} d: {} v: {} p:>".format(self.title,
                                               self.description,
                                               self.viewable,
                                               self.path)
