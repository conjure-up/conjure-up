from __future__ import unicode_literals
from urwid import (WidgetWrap, Text, Pile,
                   Filler)
from ubuntui.utils import Color, Padding


class BootstrapWaitView(WidgetWrap):
    def __init__(self, app):
        self.app = app
        _pile = [
            Padding.center_90(
                Color.info_context(Text("just waiting")))
        ]
        super().__init__(Filler(Pile(_pile), valign="middle"))
