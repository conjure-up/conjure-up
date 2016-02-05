# Copyright 2015 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
            widgets.append(Color.frame_header(Text(self._title)))
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
            self._title.set_text(val)
        else:
            self._title.set_text((attr, val))

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
            Padding.line_break(""),
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
