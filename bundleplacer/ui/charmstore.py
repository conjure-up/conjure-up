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

from enum import Enum
import logging


from urwid import (AttrMap, Button, Columns, Divider, connect_signal,
                   ListBox, Filler, BoxAdapter, Edit, Filler, Padding,
                   Pile, SimpleFocusListWalker, Text, WidgetWrap)

from ubuntui.ev import EventLoop
from ubuntui.widgets.buttons import MenuSelectButton

from bundleplacer.bundle import CharmStoreAPI

log = logging.getLogger('bundleplacer')


class CharmStoreSearchWidget(WidgetWrap):

    def __init__(self, add_cb, charmstore_column):
        self.add_cb = add_cb
        self.charmstore_column = charmstore_column
        self.api = CharmStoreAPI()
        self.search_delay_alarm = None
        self.search_text = ""
        self._search_future = None
        self._search_result = None
        self._suggested_results = None
        w = self.build_widgets()
        super().__init__(w)

    def build_widgets(self):
        self.editbox = Edit(caption=('text', "Search Charm Store: "))

        connect_signal(self.editbox, 'change',
                       self.handle_edit_changed)

        return Padding(AttrMap(self.editbox,
                               'filter', 'filter_focus'), left=2, right=2)

    def update(self):
        if self._search_future is None and self._suggested_results is None:
            self.really_search()

        if self._search_future and self._search_future.done():
            self._search_result = self._search_future.result()
            self._search_future = None

            if self._suggested_results is None:
                self._suggested_results = self._search_result
            
            # result being None indicates an error, which was handled by
            # handle_search_error.
            if self._search_result is None:
                return
            self.set_column(self._search_result['Results'])

    def set_column(self, results):
        self.charmstore_column.clear_search_results()
        for r in results:
            match_name = r['Id']
            self.charmstore_column.add_result(match_name, r)
        self.charmstore_column.update()

    def handle_edit_changed(self, sender, userdata):
        self.search_text = userdata
        self.enqueue_search()
        self.charmstore_column.handle_search_change(userdata)

    def enqueue_search(self):
        if self.search_delay_alarm:
            EventLoop.remove_alarm(self.search_delay_alarm)
        self.search_delay_alarm = EventLoop.set_alarm_in(0.5,
                                                         self.really_search)

    def really_search(self, *args, **kwargs):
        self.search_delay_alarm = None
        self._search_future = self.api.get_matches(self.search_text,
                                                   self.handle_search_error)

        def update_immediately(future):
            self.update()
            self.charmstore_column.searching = False
            self.charmstore_column.update()

        self._search_future.add_done_callback(update_immediately)

    def handle_search_error(self, e):
        self.charmstore_column.handle_error(e)

    def do_add_charm(self, sender):
        self.add_cb(self.search_text, self._search_result)


class CharmWidget(WidgetWrap):
    def __init__(self, charm_source, charm_dict, add_cb):
        self.add_cb = add_cb
        self.charm_source = charm_source
        self.charm_dict = charm_dict
        self.md = charm_dict['Meta']['charm-metadata']
        w = self.build_widgets()
        super().__init__(w)

    def selectable(self):
        return True
        
    def build_widgets(self):
        self.charm_name = self.md['Name']
        source = self.charm_source
        summary = self.md['Summary']
        s = "{} ({})\n    {}\n".format(self.charm_name, source, summary)
        return AttrMap(MenuSelectButton(s, on_press=self.handle_press),
                       'text',
                       'button_secondary focus')

    def handle_press(self, button):
        self.add_cb(self.charm_name, self.charm_dict)


class CharmstoreColumnUIState(Enum):
    RELATED = 0
    SEARCH_RESULTS = 1


class CharmstoreColumn(WidgetWrap):
    def __init__(self, display_controller, placement_controller,
                 placement_view):
        self.placement_controller = placement_controller
        self.display_controller = display_controller
        self.placement_view = placement_view
        self.state = CharmstoreColumnUIState.RELATED
        self.prev_state = None
        self.current_search_string = ""
        w = self.build_widgets()
        super().__init__(w)
        self._related_charms = []
        self._search_results = []
        self.searching = False
        self.refresh_related()
        self.update()

    def build_widgets(self):
        self.title = Text('')
        self.pile = Pile([Divider(),
                          self.title])
        return self.pile

    def refresh_related(self):
        pass

    def clear_search_results(self):
        self._search_results = []

    def handle_search_change(self, s):
        if s == "":
            self.state = CharmstoreColumnUIState.RELATED
            self.clear_search_results()
        else:
            self.state = CharmstoreColumnUIState.SEARCH_RESULTS
        self.current_search_string = s
        self.searching = True
        self.update()

    def update(self):
        opts = self.pile.options()
        self.pile.contents[2:] = [(CharmWidget(n, d, self.do_add_charm),
                                   opts) for n, d in self._search_results
                                  if 'Meta' in d]
        if self.state == CharmstoreColumnUIState.RELATED:
            #self.title.set_text("Charms Related to this Bundle")
            self.title.set_text("Popular Charms:")

        else:
            if self.searching:
                msg = "Searching for '{}'…\n".format(
                    self.current_search_string)
                self.title.set_text(msg)
            else:
                n = len(self._search_results)
                if n == 0:
                    advice = ""
                    if len(self.current_search_string) < 3:
                        advice = "Try a longer search string."
                    msg = ("No charms found matching '{}' "
                           "{}\n".format(self.current_search_string,
                                         advice))
                else:
                    msg = ("{} charms matching {}:"
                           "\n".format(n, self.current_search_string))
            self.title.set_text(msg)

    def add_result(self, charm_name, charm_dict):
        self._search_results.append((charm_name, charm_dict))

    def focus_prev_or_top(self):
        if len(self.pile.contents) > 2:
            self.pile.focus_position = 2

    def do_add_charm(self, charm_name, charm_dict):
        self.placement_view.do_add_charm(charm_name,
                                         charm_dict)

    def handle_error(self, e):
        msg = "Error searching for {}: {}".format(self.current_search_string,
                                                  e)
        self.title.set_text(msg)
