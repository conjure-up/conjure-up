""" A View to inform user that shutdown is in progress.
"""

from ubuntui.utils import Padding
from urwid import Filler, LineBox, Pile, Text, WidgetWrap


class ShutdownView(WidgetWrap):

    def __init__(self):
        message = "Conjure-up is shutting down, please wait."
        box = Padding.center_45(LineBox(Pile([
            Padding.line_break(""),
            Text(message, align="center"),
            Padding.line_break(""),
        ])))
        super().__init__(Filler(box, valign="middle"))
