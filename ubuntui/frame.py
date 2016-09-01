""" Base Frame Widget """

from urwid import Frame as _Frame
from urwid import WidgetWrap
from .anchors import Header, Footer, Body


class Frame(WidgetWrap):

    def __init__(self, header=None, body=None, footer=None):
        self.header = header if header else Header("Welcome")
        self.body = body if body else Body()
        self.footer = footer if footer else Footer()
        self.frame = _Frame(self.body,
                            header=self.header,
                            footer=self.footer)
        super().__init__(self.frame)

    def set_header(self, title=None, excerpt=None):
        self.frame.header = Header(title, excerpt)

    def set_subheader(self, text=""):
        self.frame.header.subheader = text

    def set_footer(self, message, completion=0):
        self.frame.footer = Footer(message, completion)

    def set_body(self, widget):
        self.frame.body = widget
