""" Step model
"""


class StepModel:
    def __init__(self, step):
        self.title = step.get('title', '')
        self.description = step.get('description', '')
        self.result = ''
        self.icon = ("pending_icon", "\N{BALLOT BOX}")
        self.viewable = step.get('viewable', False)
        self.path = step.get('path', None)

        self.additional_input = step.get('additional-input', [])

    def __repr__(self):
        return "<{}>".format(self.title)
