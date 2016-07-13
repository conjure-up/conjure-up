from ubuntui.utils import Padding
from urwid import WidgetWrap, Text, Filler, Pile


class BootstrapWaitView(WidgetWrap):

    def __init__(self, app):
        self.app = app
        self.text = Text("Waiting for bootstrap to finish")
        _pile = [
            Padding.center_80(self.text)
        ]
        super().__init__(Filler(Pile(_pile), valign="top"))

    def update_text(self, output):
        self.text.set_text(output)
