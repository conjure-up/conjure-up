from ubuntui.utils import Padding
from urwid import WidgetWrap, Text, Filler, Pile


class SummaryView(WidgetWrap):

    def __init__(self, app, results):
        self.app = app
        self.results = "\n".join(results)
        _pile = [
            Padding.center_80(Text(self.results))
        ]
        super().__init__(Filler(Pile(_pile), valign="top"))
