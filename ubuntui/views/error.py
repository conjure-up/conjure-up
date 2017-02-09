""" An exception View equipped with traceback,
log output, and where to file a bug.
"""

from urwid import (ExitMainLoop, Pile, Text, Filler, WidgetWrap, Divider)
from ubuntui.widgets.buttons import cancel_btn
from ubuntui.utils import Color, Padding
import sys


class ErrorViewException(Exception):
    "Problem in Error  View"


class ErrorView(WidgetWrap):

    def __init__(self, error):
        body = [
            Padding.center_60(
                Text("Oops, there was a problem with your install:",
                     align="center")),
            Padding.center_95(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)),
            Padding.center_85(Text("Reason:")),
            Padding.center_80(Color.error_major(Text(error))),
            Padding.line_break(""),
            Padding.line_break(""),
            Padding.center_95(
                Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}", 1, 1)),
            Padding.center_20(self._build_buttons())
        ]
        super().__init__(Filler(Pile(body), valign="middle"))

    def _build_buttons(self):
        buttons = [
            Color.button_secondary(
                cancel_btn(label="Quit", on_press=self.cancel),
                focus_map="button_secondary focus")
        ]
        return Pile(buttons)

    def cancel(self, button):
        raise ExitMainLoop()
