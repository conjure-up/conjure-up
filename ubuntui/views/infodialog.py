from urwid import (WidgetWrap, Button, LineBox, Pile, Text)


class InfoDialogWidget(WidgetWrap):

    """A widget that displays a message and a close button."""

    def __init__(self, message, close_func):
        self.close_func = close_func
        button = Button("Close", self.do_close)
        box = LineBox(Pile([Text(message),
                            button]),
                      title="Info")
        super().__init__(box)

    def do_close(self, sender):
        self.close_func(self)
