""" Step widget, attaches properties from steps to urwid Text widgets
"""

from urwid import Text
from conjure.controllers.steps import common


class StepWidget:
    def __init__(self, step):
        self.step = step
        self.title = Text(common.parse_title(self.step))
        self.description = Text(common.parse_description(self.step))
        self.result = Text('')
        self.icon = Text(("pending_icon", "\N{HOURGLASS}"))
