""" A View to inform user that shutdown is in progress.
"""

from ubuntui.utils import Padding
from urwid import Columns, LineBox, Pile, Text, WidgetWrap

from conjureup import events
from conjureup.app_config import app
from conjureup.ui.widgets.buttons import SubmitButton


class ShutdownView(WidgetWrap):

    def __init__(self, exit_code):
        self.exit_code = exit_code
        self.message = Text('Do you want to quit?', align='center')
        super().__init__(LineBox(Pile([
            Padding.line_break(""),
            self.message,
            Padding.line_break(""),
            Columns([
                Text(""),
                SubmitButton('Yes', lambda _: self.confirm()),
                Text(""),
                SubmitButton('No', lambda _: self.cancel()),
                Text(""),
            ]),
            Padding.line_break(""),
        ])))

    def confirm(self):
        self.message.set_text("Conjure-up is shutting down, please wait.")
        del self._w.base_widget.contents[-2:]  # remove buttons
        events.Shutdown.set(self.exit_code)

    def cancel(self):
        app.ui.hide_shutdown_dialog()

    def keypress(self, size, key):
        if key == 'tab':
            result = super().keypress(size, 'right')
            if result == 'right':
                result = super().keypress(size, 'left')
            return result
        return super().keypress(size, key)
