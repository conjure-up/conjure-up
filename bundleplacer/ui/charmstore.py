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
from enum import Enum

from urwid import (
    AttrMap,
    Edit,
    Padding,
    Pile,
    Text,
    WidgetWrap,
    connect_signal
)

from bundleplacer.charmstore_api import CharmStoreAPI, CharmStoreID
from ubuntui.ev import EventLoop
from ubuntui.widgets.buttons import MenuSelectButton

log = logging.getLogger('bundleplacer')


class CharmStoreSearchWidget(WidgetWrap):

    def __init__(self, add_cb, charmstore_column, config, series):
        self.add_cb = add_cb
        self.charmstore_column = charmstore_column
        self.config = config
        self.api = CharmStoreAPI(series=series)
        self.search_delay_alarm = None
        self.search_text = ""
        self._search_future = None
        self._search_result = None
        self._popular_results = None
        w = self.build_widgets()
        super().__init__(w)
        # populate popular_results with an initial search
        self.really_search()

    def build_widgets(self):
        self.editbox = Edit(caption=('text', "Search Charm Store: "))

        connect_signal(self.editbox, 'change',
                       self.handle_edit_changed)

        return Padding(AttrMap(self.editbox,
                               'filter', 'filter_focus'), left=2, right=2)

    def _handle_search_done(self, future):
        assert(future == self._search_future)
        self._search_result = self._search_future.result()
        self._search_future = None

        if self._popular_results is None:
            self._popular_results = self._search_result

        # result being None indicates an error, which was handled by
        # handle_search_error.
        if self._search_result:
            br, cr = self._search_result
            self.set_column(br, cr)
        self.charmstore_column.loading = False
        self.charmstore_column.update()

    def set_column(self, bundle_results, charm_results):
        self.charmstore_column.clear_search_results()
        self.charmstore_column.add_results(bundle_results, charm_results)
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
        self._search_future.add_done_callback(self._handle_search_done)

    def handle_search_error(self, e):
        self.charmstore_column.handle_error(e)

    def do_add_charm(self, sender):
        self.add_cb(self.search_text, self._search_result)


class CharmWidget(WidgetWrap):

    def __init__(self, charm_dict, add_cb, recommended=False):
        self.charm_dict = charm_dict
        self.add_cb = add_cb
        self.recommended = recommended
        self.header = None
        self.charm_source = charm_dict['Id']
        self.md = charm_dict['Meta']['charm-metadata']
        self.charm_name = self.md['Name']
        w = self.build_widgets()
        super().__init__(w)

    def selectable(self):
        return True

    def set_header(self, header):
        self.header = header
        self._w = self.build_widgets()

    def build_widgets(self):
        self.charm_name = self.md['Name']
        summary = self.md['Summary']
        top = []
        pad = 0
        if self.header:
            top = [Text("\n{}\n".format(self.header))]
        if self.recommended:
            pad = 2
        s = "{} ({})\n  {}\n".format(self.charm_name,
                                     self.charm_source,
                                     summary)
        b = MenuSelectButton(s, on_press=self.handle_press)
        return Pile(top + [AttrMap(Padding(b, left=pad),
                                   'text',
                                   'button_secondary focus')])

    def handle_press(self, button):
        self.add_cb(self.charm_name, self.charm_dict)


class BundleWidget(WidgetWrap):

    def __init__(self, bundle_dict, add_cb):
        self.add_cb = add_cb
        self.bundle_source = bundle_dict['Id']
        self.bundle_dict = bundle_dict
        self.header = None
        self.md = bundle_dict['Meta']['bundle-metadata']
        w = self.build_widgets()
        super().__init__(w)

    def selectable(self):
        return True

    def set_header(self, header):
        self.header = header
        self._w = self.build_widgets()

    def build_widgets(self):
        name_with_rev = self.bundle_source.split("/")[-1]
        bundle_name = "-".join(name_with_rev.split("-")[:-1])

        if 'Machines' in self.md:
            summary = ("{} services "
                       "on {} machines").format(len(self.md['Services']),
                                                len(self.md['Machines']))
        else:
            summary = "{} services".format(len(self.md['Services']))
        s = "{} ({})\n    {}\n".format(bundle_name, self.bundle_source,
                                       summary)

        top = []
        if self.header:
            top = [Text("\n{}\n".format(self.header))]

        b = MenuSelectButton(s, on_press=self.handle_press)
        return Pile(top + [AttrMap(b,
                                   'text',
                                   'button_secondary focus')])

    def handle_press(self, button):
        self.add_cb(self.md)


class CharmstoreColumnUIState(Enum):
    RELATED = 0
    SEARCH_RESULTS = 1


class CharmstoreColumn(WidgetWrap):

    def __init__(self, display_controller, placement_controller,
                 placement_view, metadata_controller):
        self.placement_controller = placement_controller
        self.display_controller = display_controller
        self.placement_view = placement_view
        self.metadata_controller = metadata_controller
        self.state = CharmstoreColumnUIState.RELATED
        self.prev_state = None
        self.current_search_string = ""
        w = self.build_widgets()
        super().__init__(w)
        self._related_charms = []
        self._bundle_results = []
        self._charm_results = []
        self._recommended_charms = []
        self.loading = True
        self.update()

    def build_widgets(self):
        self.title = Text('')
        self.pile = Pile([self.title])
        return self.pile

    def clear_search_results(self):
        self._bundle_results = []
        self._charm_results = []

    def handle_search_change(self, s):
        if s == "":
            self.state = CharmstoreColumnUIState.RELATED
            self.clear_search_results()
        else:
            self.state = CharmstoreColumnUIState.SEARCH_RESULTS
        self.current_search_string = s
        self.loading = True
        self.update()

    def remove_existing_charms(self, charms):
        existing_charms = [CharmStoreID(s.charm_source).as_str_without_rev()
                           for s in
                           self.placement_controller.bundle.services]
        return [c for c in charms
                if CharmStoreID(c['Id']).as_str_without_rev()
                not in existing_charms]

    def get_filtered_recommendations(self):
        opts = self.pile.options()
        if len(self._recommended_charms) == 0:
            mc = self.metadata_controller
            self._recommended_charms = mc.get_recommended_charms()
        return [(CharmWidget(d, self.do_add_charm, recommended=True), opts)
                for d in self.remove_existing_charms(self._recommended_charms)]

    def update(self):
        opts = self.pile.options()
        extra_widgets = []
        recommended_widgets = []
        if self.metadata_controller.loaded():
            recommended_widgets = self.get_filtered_recommendations()
            if len(recommended_widgets) > 0:
                top_w = recommended_widgets[0][0]
                top_w.set_header("Recommended Charms")

            self.loading = False

        series = self.placement_controller.bundle.series
        bundle_widgets = [(BundleWidget(d, self.do_add_bundle),
                           opts) for d in self._bundle_results
                          if 'bundle-metadata' in d.get('Meta', {}) and
                          'Series' in d['Meta']['bundle-metadata'] and
                          d['Meta']['bundle-metadata']['Series'] == series]

        if len(bundle_widgets) > 0:
            top_w = bundle_widgets[0][0]
            top_w.set_header("Bundles")

        filtered_charm_results = self.remove_existing_charms(
            self._charm_results)
        filtered_charm_results = filtered_charm_results[:10]

        charm_widgets = [(CharmWidget(d, self.do_add_charm),
                          opts) for d in filtered_charm_results
                         if 'charm-metadata' in d.get('Meta', {})]
        if len(charm_widgets) > 0:
            top_w = charm_widgets[0][0]
            top_w.set_header("Charms")

        if self.state == CharmstoreColumnUIState.RELATED:
            if self.loading:
                self.title.set_text("\nLoading Recommended "
                                    "and Popular Charms…")
            else:
                self.title.set_text("")
            extra_widgets = recommended_widgets
        else:
            if self.loading:
                msg = "\nSearching for '{}'…\n".format(
                    self.current_search_string)
                self.title.set_text(msg)
            else:
                bn = len(self._bundle_results)
                cn = len(filtered_charm_results)
                if bn + cn == 0:
                    advice = ""
                    if len(self.current_search_string) < 3:
                        advice = "Try a longer search string."
                    msg = ("\nNo charms found matching '{}' "
                           "{}".format(self.current_search_string,
                                       advice))
                else:
                    msg = ("\nShowing the top {} bundles and {} "
                           "charms matching {}:"
                           "".format(bn, cn, self.current_search_string))
            self.title.set_text(msg)

        self.pile.contents[1:] = extra_widgets + bundle_widgets + charm_widgets

    def add_results(self, bundle_results, charm_results):
        self._bundle_results += bundle_results
        self._bundle_results = self._bundle_results[:5]
        self._charm_results += charm_results

    def focus_prev_or_top(self):
        if len(self.pile.contents) < 2:
            return
        if self.state == CharmstoreColumnUIState.RELATED and self.loading \
           and len(self.pile.contents) > 2:
            self.pile.focus_position = 2
        else:
            self.pile.focus_position = 1

    def do_add_charm(self, charm_name, charm_dict):
        self.placement_view.do_add_charm(charm_name,
                                         charm_dict)
        self.update()

    def do_add_bundle(self, bundle_dict):
        self.placement_view.do_add_bundle(bundle_dict)

    def handle_error(self, e):
        msg = "Error searching for {}: {}".format(self.current_search_string,
                                                  e)
        self.title.set_text(msg)
