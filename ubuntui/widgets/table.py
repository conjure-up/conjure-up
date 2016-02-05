# Copyright 2014, 2015 Canonical, Ltd.
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

from __future__ import unicode_literals

from urwid import (Columns, Pile, Divider)


class Cols:

    def __init__(self):
        self.columns = []

    def add(self, widget, width=None):
        """ Add a widget to a columns list

        Arguments:
        widget: widget
        width: width of column
        """
        if width is None:
            self.columns.append(widget)
        else:
            self.columns.append(('fixed', width, widget))

    def render(self):
        """ Renders columns with proper spacing
        """
        return Columns(self.columns)


class Table:
    def __init__(self):
        self.rows = Pile([])

    def append(self, item):
        """ Appends widget to Pile
        """
        self.rows.append((item, self.rows.options()))
        self.rows.append((
            Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}"),
            self.rows.options()))

    def render(self):
        return self.rows
