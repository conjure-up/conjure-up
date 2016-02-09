from __future__ import unicode_literals

from urwid import (Columns, Pile, Divider)
from ubuntui.utils import Color


class Table:
    def __init__(self):
        self.rows = Pile([])

    def addHeadings(self, headings):
        """ Takes list of headings and converts them to column header
        with appropriate color

        Params:
        headings: List of column text headings
        """
        cols = []
        for h in headings:
            h = Color.column_header(h)
            cols.append(h)
            cols.append(('fixed', 1,
                         Color.column_header(
                             Divider("\N{BOX DRAWINGS LIGHT VERTICAL}"))))
        self.addRow(Columns(cols))

    def addColumns(self, columns):
        cols = []
        for c in columns:
            cols.append(c)
            cols.append(('fixed', 1,
                         Divider("\N{BOX DRAWINGS LIGHT VERTICAL}")))
        self.addRow(Columns(cols))

    def addRow(self, item):
        """ Appends widget to Pile
        """
        self.rows.contents.append((item, self.rows.options()))
        self.rows.contents.append((
            Divider("\N{BOX DRAWINGS LIGHT HORIZONTAL}"),
            self.rows.options()))

    def render(self):
        return self.rows
