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

    def __init__(self, title=None, excerpt=None, align="left"):
        self._title = title
        self._excerpt = excerpt
        widgets = []
        if self._title is not None:
            widgets.append(Color.frame_header(Padding.line_break("")))
            widgets.append(Color.frame_header(
                Padding.left(Text(self._title.upper()), left=2)))
            widgets.append(Color.frame_header(Padding.line_break("")))
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


class Footer(WidgetWrap):
    """ Footer widget
    Style key: `frame_footer`
    """

    def __init__(self, message="", completion=0):
        message_widget = (Text(message, align="center"))
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
