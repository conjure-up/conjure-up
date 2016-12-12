# Copyright 2014 Canonical, Ltd.
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

import logging

from urwid import (
    AttrMap,
    Columns,
    Edit,
    Pile,
    Text,
    WidgetWrap,
    connect_signal
)

log = logging.getLogger('bundleplacer')


class FilterBox(WidgetWrap):

    def __init__(self, edit_changed_cb, label="", info_text=""):
        self.label = Text(label)
        self.info_text = Text(info_text)
        self.editbox = Edit(caption=('text', "Filter: "))
        connect_signal(self.editbox, 'change',
                       edit_changed_cb)

        w = Pile([Columns([AttrMap(self.editbox,
                                   'filter', 'filter_focus')])
                  # self.info_text  # -- WORKAROUND for issue #194
                  ])
        super().__init__(w)

    def set_info(self, n_showing, n_total):
        m = ["Filter ", ('label', "({} of {} shown): ".format(n_showing,
                                                              n_total))]
        self.editbox.set_caption(m)
        if False:   # WORKAROUND for issue #194
            t = ''
        else:
            t = ('label',
                 "  Filter on hostname or hardware info like 'cores:4'")
        self.info_text.set_text(t)
