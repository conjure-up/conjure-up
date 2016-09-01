from __future__ import unicode_literals

from urwid import (Columns, ListBox)
from ubuntui.widgets.hr import HR


class Table:

    def __init__(self):
        self._rows = []
        self._row_id = []
        self._is_header_set = False

    def addHeadings(self, headings):
        """ Takes list of headings and converts them to column header
        with appropriate color

        Params:
        headings: List of column text headings
        """
        if not self._is_header_set:
            self.addRow(Columns(headings), False)
            self._is_header_set = True

    def addColumns(self, row_id, columns, dividechars=1, force=False):
        """ Convert list of widgets to Columns and add to a table row

        Arguments:
        row_id: unique id of new row
        columns: list of columns
        dividechars: character space between columns
        force: force additional row regardless of existing row_id
        """
        if row_id not in self._row_id or force:
            if row_id not in self._row_id:
                self._row_id.append(row_id)

            # If we force an additional row it's usually to expand
            # on the previous row so we do not display a divider
            # between the two.
            use_divider = True
            if force:
                use_divider = False
            self.addRow(Columns(columns, dividechars=dividechars), use_divider)

    def addRow(self, item, use_divider=True):
        """ Appends widget to Pile

        Arguments:
        item: Widget to add to listbox
        use_divider: use divider for row item
        """
        if use_divider and len(self._rows) != 0:
            self._rows.append(HR(0, 0))
        self._rows.append(item)

    def render(self):
        return ListBox(self._rows)
