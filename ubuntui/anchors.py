from urwid import Pile, Text, WidgetWrap

from .lists import SimpleList
from .utils import Padding, Color


class Header(WidgetWrap):
    """ Header Widget

    This widget uses the style key `frame_header`

    Arguments:
    title: Title text
    excerpt: Additional header text
    align: Text alignment, defaults=left
    """
    def __init__(self, title=None, excerpt=None, subheader="", align="left"):
        self._title = title
        self._excerpt = excerpt
        self._subheader = Text(subheader, align='center')
        widgets = []
        if self._title is not None:
            widgets.append(Color.frame_header(Text(self._title.upper())))
        widgets.append(Color.frame_subheader(self._subheader))
        if self._excerpt is not None:
            widgets.append(Text(""))
            widgets.append(
                Padding.center_90(
                    Text(("body", self._excerpt))))
            widgets.append(Text(""))
        super().__init__(Pile(widgets))

    @property
    def title(self):
        return self._title.get_text()[0]

    @title.setter
    def title(self, val, attr=None):
        """
        Sets header title text

        Arguments:
        val: Text value
        attr: (optional) Attribute lookup
        """
        if attr is not None:
            self._title.set_text(val.upper())
        else:
            self._title.set_text((attr, val.upper()))

    @property
    def subheader(self):
        return self._subheader.get_text()[0]

    @subheader.setter
    def subheader(self, val):
        self._subheader.set_text(val)


class Footer(WidgetWrap):
    """ Footer widget
    Style key: `frame_footer`
    """

    def __init__(self, message="", completion=0):
        message_widget = (Text(message))
        status = [
            message_widget
        ]
        super().__init__(Color.frame_footer(Pile(status)))


class Body(WidgetWrap):
    """ Body widget
    """

    def __init__(self):
        text = [
            Padding.line_break(""),
        ]
        w = (SimpleList(text))
        super().__init__(w)
