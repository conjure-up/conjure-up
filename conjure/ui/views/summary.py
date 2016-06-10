from ubuntui.utils import Padding
from urwid import WidgetWrap, Text, Filler, Pile


class SummaryView(WidgetWrap):

    def __init__(self, app, output):
        self.app = app
        _pile = [
            Padding.center_80(Text(output))
        ]
        super().__init__(Filler(Pile(_pile), valign="top"))
