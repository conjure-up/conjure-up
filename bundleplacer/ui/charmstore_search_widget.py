# Copyright 2016 Canonical, Ltd.
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

from urwid import (AttrMap, Button, Columns, connect_signal, Edit,
                   Padding, Pile, SelectableIcon, Text, WidgetWrap)

from bundleplacer.bundle import CharmStoreAPI


log = logging.getLogger('bundleplacer')


class CharmStoreSearchWidget(WidgetWrap):

    def __init__(self, add_cb):
        self.add_cb = add_cb
        self.api = CharmStoreAPI()
        self.search_text = ""
        self._search_future = None
        self._search_result = None
        w = self.build_widgets()
        super().__init__(w)

    def build_widgets(self):
        self.info_text = Text("")
        self.editbox = Edit()

        connect_signal(self.editbox, 'change',
                       self.handle_edit_changed)

        self.do_search_button = AttrMap(Button("Search Charm Store",
                                               on_press=self.do_search),
                                        'button_secondary',
                                        'button_secondary focus')
        self.add_charm_dummy = AttrMap(SelectableIcon("(Add new charm)"),
                                       'disabled_button',
                                       'disabled_button_focus')
        self.add_charm_button = AttrMap(Button("Add",
                                               on_press=self.do_add_charm),
                                        'button_secondary',
                                        'button_secondary focus')
        self.top = Columns([AttrMap(self.editbox,
                                    'filter', 'filter_focus'),
                            (22, self.do_search_button)], dividechars=2)
        self.bottom = Columns([self.info_text,
                               (22, self.add_charm_dummy)], dividechars=2)

        return Padding(Pile([self.top, self.bottom]), left=6)

    def update(self):
        if self._search_future and self._search_future.done():
            self._search_result = self._search_future.result()
            self._search_future = None

            # result being None indicates an error, which was handled by
            # handle_search_error.
            if self._search_result is not None:
                meta = self._search_result['Meta']['charm-metadata']
                summary = meta['Summary']
                self.info_text.set_text(summary)
                _, opts = self.bottom.contents[-1]
                self.bottom.contents[-1] = (self.add_charm_button,
                                            opts)
            return

        if self._search_future is None and self._search_result is None:
            _, opts = self.bottom.contents[-1]
            self.bottom.contents[-1] = (self.add_charm_dummy,
                                        opts)

    def handle_edit_changed(self, sender, userdata):
        self.search_text = userdata

    def do_search(self, sender):
        self._search_future = None

        if self.search_text == "":
            return

        self._search_future = self.api.get_entity(self.search_text,
                                                  self.handle_search_error)
        self.info_text.set_text("Searching…")

    def handle_search_error(self, e):
        self.info_text.set_text("{} not found.".format(self.search_text))

    def do_add_charm(self, sender):
        self.add_cb(self.search_text, self._search_result)
