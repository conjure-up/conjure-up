# Copyright 2014-2016 Canonical, Ltd.
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
from operator import attrgetter
from subprocess import Popen, PIPE, TimeoutExpired

from urwid import (AttrMap, Columns, Divider, Filler, Overlay,
                   GridFlow, Frame, Padding, Pile, Text, WidgetWrap)

from ubuntui.widgets.buttons import PlainButton, MenuSelectButton
from ubuntui.views import InfoDialogWidget
from ubuntui.widgets import MetaScroll
from ubuntui.widgets.hr import HR

from bundleplacer.charmstore_api import MetadataController
from bundleplacer.ui.charmstore import CharmstoreColumn, CharmStoreSearchWidget
from bundleplacer.ui.filter_box import FilterBox
from bundleplacer.ui.services_column import ServicesColumn
from bundleplacer.ui.machines_column import MachinesColumn
from bundleplacer.ui.relations_column import RelationsColumn
from bundleplacer.ui.options_column import OptionsColumn
from bundleplacer.grapher import graph_for_bundle, scc_graph_for_bundle
from bundleplacer.charmstore_api import CharmStoreID

log = logging.getLogger('bundleplacer')


BUTTON_SIZE = 20


class UIState(Enum):
    PLACEMENT_EDITOR = 0
    RELATION_EDITOR = 1
    CHARMSTORE_VIEW = 2         # This is the default
    OPTIONS_EDITOR = 3


class PlacementView(WidgetWrap):

    """
    Handles display of machines and services.

    displays nothing if self.controller is not set.
    set it to a PlacementController.

    :param do_deploy_cb: deploy callback from controller
    """

    def __init__(self, display_controller, placement_controller,
                 config, do_deploy_cb,
                 initial_state=UIState.CHARMSTORE_VIEW,
                 has_maas=False):
        self.display_controller = display_controller
        self.placement_controller = placement_controller
        self.config = config
        self.do_deploy_cb = do_deploy_cb
        self.state = initial_state
        self.has_maas = has_maas
        self.prev_state = None
        self.showing_overlay = False
        self.showing_graph_split = False
        self.show_scc_graph = False
        self.bundle = placement_controller.bundle
        self.metadata_controller = MetadataController(self.bundle, config)
        w = self.build_widgets()
        super().__init__(w)
        self.reset_selections(top=True)  # calls self.update

    def scroll_down(self):
        pass

    def scroll_up(self):
        pass

    def focus_footer(self):
        self.frame.focus_position = 'footer'
        self.footer_grid.focus_position = 1

    def handle_tab(self, backward):
        tabloop = ['headercol1', 'col1', 'headercol2', 'col2', 'footer']

        if not self.has_maas:
            tabloop.remove('headercol1')

        def goto_header_col1():
            self.frame.focus_position = 'header'
            self.header_columns.focus_position = 0

        def goto_header_col2():
            self.frame.focus_position = 'header'
            self.header_columns.focus_position = 1

        def goto_col1():
            self.frame.focus_position = 'body'
            self.columns.focus_position = 0

        def goto_col2():
            self.frame.focus_position = 'body'
            if self.state == UIState.PLACEMENT_EDITOR:
                self.focus_machines_column()
            elif self.state == UIState.RELATION_EDITOR:
                self.focus_relations_column()
            elif self.state == UIState.OPTIONS_EDITOR:
                self.focus_options_column()
            else:
                self.focus_charmstore_column()

        actions = {'headercol1': goto_header_col1,
                   'headercol2': goto_header_col2,
                   'col1': goto_col1,
                   'col2': goto_col2,
                   'footer': self.focus_footer}

        if self.frame.focus_position == 'header':
            cur = ['headercol1',
                   'headercol2'][self.header_columns.focus_position]
        elif self.frame.focus_position == 'footer':
            cur = 'footer'
        else:
            cur = ['col1', 'col2'][self.columns.focus_position]

        cur_idx = tabloop.index(cur)

        if backward:
            next_idx = cur_idx - 1
        else:
            next_idx = (cur_idx + 1) % len(tabloop)

        actions[tabloop[next_idx]]()

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self.handle_tab('shift' in key)
            return key

        unhandled_key = self._w.keypress(size, key)
        if unhandled_key is None:
            return None
        elif unhandled_key in ['g', 'G']:
            if unhandled_key == 'G':
                self.show_scc_graph = True
            else:
                self.show_scc_graph = False
            self.showing_graph_split = not self.showing_graph_split
            if self.showing_graph_split:
                opts = self.placement_edit_body_pile.options()
                self.placement_edit_body_pile.contents.insert(
                    0, (self.bundle_graph_widget, opts))
            else:
                self.placement_edit_body_pile.contents.pop(0)
            self.update()
        else:
            return unhandled_key

    def get_services_header(self):
        b = PlainButton("Clear All Placements",
                        on_press=self.do_clear_all)
        self.clear_all_button = AttrMap(b,
                                        'button_secondary',
                                        'button_secondary focus')

        self.services_buttons = [self.clear_all_button]
        self.services_button_grid = GridFlow(self.services_buttons,
                                             36, 1, 0, 'center')

        ws = [Divider(), Text(("body", "Services"), align='center'),
              Divider()]
        if self.has_maas:
            ws.append(self.services_button_grid)

        return Pile(ws)

    def get_charmstore_header(self, charmstore_column):
        series = self.placement_controller.bundle.series
        self.charm_search_widget = CharmStoreSearchWidget(self.do_add_charm,
                                                          charmstore_column,
                                                          self.config,
                                                          series)
        self.charm_search_header_pile = Pile([Divider(),
                                              Text(("body", "Add Charms"),
                                                   align='center'),
                                              Divider(),
                                              self.charm_search_widget])

        return self.charm_search_header_pile

    def get_machines_header(self, machines_column):
        b = PlainButton("Open in Browser",
                        on_press=self.browse_maas)
        self.open_maas_button = AttrMap(b,
                                        'button_secondary',
                                        'button_secondary focus')
        self.maastitle = Text("Connected to MAAS")
        maastitle_widgets = Padding(Columns([self.maastitle,
                                             (22, self.open_maas_button)]),
                                    align='center',
                                    width='pack', left=2,
                                    right=2)

        f = machines_column.machines_list.handle_filter_change
        self.filter_edit_box = FilterBox(f)
        pl = [Divider(),
              Text(('body',
                    "Ready Machines {}".format(MetaScroll().get_text()[0])),
                   align='center'),
              Divider(),
              maastitle_widgets,
              Divider(),
              self.filter_edit_box]

        self.machines_header_pile = Pile(pl)
        return self.machines_header_pile

    def update_machines_header(self):
        maasinfo = self.placement_controller.maasinfo
        maasname = "'{}' <{}>".format(maasinfo['server_name'],
                                      maasinfo['server_hostname'])
        self.maastitle.set_text("Connected to MAAS {}".format(maasname))

    def _simple_header_widgets(self, title):
        b = PlainButton("Back to Charm Store",
                        on_press=self.show_default_view)
        self.back_to_mainview_button = AttrMap(b, 'button_secondary',
                                               'button_secondary focus')
        button_grid = GridFlow([self.back_to_mainview_button],
                               36, 1, 0, 'center')

        return [Divider(),
                Text(('body', title), align='center'),
                Divider(), button_grid]

    def get_relations_header(self):
        return Pile(self._simple_header_widgets("Relation Editor"))

    def get_options_header(self, options_column):
        simple_widgets = self._simple_header_widgets("Options Editor")
        fb = FilterBox(options_column.handle_filter_change,
                       info_text="Filter by option name")
        padded_fb = Padding(AttrMap(fb, 'filter', 'filter_focus'),
                            left=2, right=2)
        return Pile(simple_widgets + [padded_fb])

    def build_widgets(self):

        self.services_column = ServicesColumn(self.display_controller,
                                              self.placement_controller,
                                              self)

        self.machines_column = MachinesColumn(self.display_controller,
                                              self.placement_controller,
                                              self)
        self.relations_column = RelationsColumn(self.display_controller,
                                                self.placement_controller,
                                                self,
                                                self.metadata_controller)
        self.charmstore_column = CharmstoreColumn(self.display_controller,
                                                  self.placement_controller,
                                                  self,
                                                  self.metadata_controller)
        self.options_column = OptionsColumn(self.display_controller,
                                            self.placement_controller,
                                            self,
                                            self.metadata_controller)

        self.machines_header = self.get_machines_header(self.machines_column)
        self.relations_header = self.get_relations_header()
        self.services_header = self.get_services_header()
        self.charmstore_header = self.get_charmstore_header(
            self.charmstore_column)
        self.options_header = self.get_options_header(self.options_column)

        cs = [self.services_header, self.charmstore_header]

        self.header_columns = Columns(cs, dividechars=2)

        self.columns = Columns([self.services_column,
                                self.machines_column], dividechars=2)

        self.deploy_button = MenuSelectButton("\nCommit\n",
                                              on_press=self.do_deploy)
        self.deploy_button_label = Text("Some charms use default")
        self.placement_edit_body_pile = Pile([self.columns])
        self.placement_edit_body = Filler(Padding(
            self.placement_edit_body_pile,
            align='center',
            width=('relative', 95)),
            valign='top')
        self.bundle_graph_text = Text("No graph to display yet.")
        self.bundle_graph_widget = Padding(self.bundle_graph_text,
                                           'center', 'pack')
        b = AttrMap(self.deploy_button,
                    'frame_header',
                    'button_primary focus')
        self.footer_grid = GridFlow([self.deploy_button_label,
                                     Padding(b, width=28,
                                             align='center')],
                                    28, 1, 1, 'right')
        f = AttrMap(self.footer_grid,
                    'frame_footer',
                    'frame_footer')

        self.frame = Frame(header=Pile([self.header_columns, HR()]),
                           body=self.placement_edit_body,
                           footer=f)
        return self.frame

    def update(self):
        if self.prev_state != self.state:
            h_opts = self.header_columns.options()
            c_opts = self.columns.options()

            if self.state == UIState.PLACEMENT_EDITOR:
                self.update_machines_header()
                self.header_columns.contents[-1] = (self.machines_header,
                                                    h_opts)
                self.columns.contents[-1] = (self.machines_column, c_opts)

            elif self.state == UIState.RELATION_EDITOR:
                self.header_columns.contents[-1] = (self.relations_header,
                                                    h_opts)
                self.columns.contents[-1] = (self.relations_column, h_opts)
            elif self.state == UIState.CHARMSTORE_VIEW:
                self.header_columns.contents[-1] = (self.charmstore_header,
                                                    h_opts)
                self.columns.contents[-1] = (self.charmstore_column, h_opts)
            elif self.state == UIState.OPTIONS_EDITOR:
                self.header_columns.contents[-1] = (self.options_header,
                                                    h_opts)
                self.columns.contents[-1] = (self.options_column, h_opts)

            self.prev_state = self.state

        self.services_column.update()

        if self.state == UIState.PLACEMENT_EDITOR:
            self.machines_column.update()
        elif self.state == UIState.RELATION_EDITOR:
            self.relations_column.update()
        elif self.state == UIState.OPTIONS_EDITOR:
            self.options_column.update()
        else:
            self.charmstore_column.update()

        unplaced = self.placement_controller.unassigned_undeployed_services()
        all = self.placement_controller.services()
        n_subs_in_unplaced = len([c for c in unplaced if c.subordinate])
        n_subs_in_all = len([c for c in all if c.subordinate])

        n_total = len(all) - n_subs_in_all
        remaining = len(unplaced) - n_subs_in_unplaced
        if remaining > 0:
            dmsg = "\nAuto-assigning {}/{} services".format(remaining,
                                                            n_total)
        else:
            dmsg = ""
        self.deploy_button_label.set_text(dmsg)

        if self.showing_graph_split:
            bundle = self.placement_controller.bundle
            if self.show_scc_graph:
                gtext = scc_graph_for_bundle(bundle, self.metadata_controller)
            else:
                gtext = graph_for_bundle(bundle, self.metadata_controller)
            if gtext == "":
                gtext = "No graph to display yet."
            self.bundle_graph_text.set_text(gtext)

    def browse_maas(self, sender):

        bc = self.config.juju_env['bootstrap-config']
        try:
            p = Popen(["sensible-browser", bc['maas-server']],
                      stdout=PIPE, stderr=PIPE)
            outs, errs = p.communicate(timeout=5)

        except TimeoutExpired:
            # went five seconds without an error, so we assume it's
            # OK. Don't kill it, just let it go:
            return
        e = errs.decode('utf-8')
        msg = "Error opening '{}' in a browser:\n{}".format(bc['name'], e)

        w = InfoDialogWidget(msg, self.remove_overlay)
        self.show_overlay(w)

    def do_clear_all(self, sender):
        self.placement_controller.clear_all_assignments()

    def do_add_charm(self, charm_name, charm_dict):
        """Add new service and focus its widget.

        """
        assert(self.state == UIState.CHARMSTORE_VIEW)

        def done_cb(f):
            csid = CharmStoreID(charm_dict['Id'])
            id_no_rev = csid.as_str_without_rev()
            info = self.metadata_controller.get_charm_info(id_no_rev,
                                                           lambda _: None)
            is_subordinate = info["Meta"]["charm-metadata"].get(
                "Subordinate", False)
            service_name = self.placement_controller.add_new_service(
                charm_name, charm_dict, is_subordinate=is_subordinate)
            self.frame.focus_position = 'body'
            self.columns.focus_position = 0
            self.update()
            self.services_column.select_service(service_name)

        # TODO MMCC: need a 'loading' indicator to start here
        self.metadata_controller.load([charm_dict['Id']], done_cb)

    def do_add_bundle(self, bundle_dict):
        assert(self.state == UIState.CHARMSTORE_VIEW)
        _, new_services, _ = self.placement_controller.merge_bundle(
            bundle_dict)
        self.frame.focus_position = 'body'
        self.columns.focus_position = 0
        charms = list(set([s.charm_source for s in new_services]))
        self.metadata_controller.load(charms)
        self.update()
        ss = sorted(new_services,
                    key=attrgetter('service_name'))
        first_service = ss[0].service_name
        self.services_column.select_service(first_service)

    def do_clear_machine(self, sender, machine):
        self.placement_controller.clear_assignments(machine)

    def clear_selections(self):
        self.services_column.clear_selections()
        self.machines_column.clear_selections()

    def reset_selections(self, top=False):
        self.clear_selections()
        self.state = UIState.CHARMSTORE_VIEW
        self.update()
        self.columns.focus_position = 0

        if top:
            self.services_column.focus_top()
        else:
            self.services_column.focus_next()

    def focus_machines_column(self):
        self.columns.focus_position = 1
        self.machines_column.focus_prev_or_top()

    def focus_relations_column(self):
        self.columns.focus_position = 1
        self.relations_column.focus_prev_or_top()

    def focus_options_column(self):
        self.columns.focus_position = 1
        self.options_column.focus_prev_or_top()

    def focus_charmstore_column(self):
        self.columns.focus_position = 1
        self.charmstore_column.focus_prev_or_top()

    def edit_placement(self):
        self.state = UIState.PLACEMENT_EDITOR
        self.update()
        self.focus_machines_column()

    def show_default_view(self, *args):
        self.state = UIState.CHARMSTORE_VIEW
        self.update()

    def edit_relations(self, service):
        self.state = UIState.RELATION_EDITOR
        self.relations_column.set_service(service)
        self.update()
        self.focus_relations_column()

    def edit_options(self, service):
        self.state = UIState.OPTIONS_EDITOR
        self.options_column.set_service(service)
        self.update()
        self.focus_options_column()

    def do_deploy(self, sender):
        self.do_deploy_cb()

    def show_overlay(self, overlay_widget):
        if not self.showing_overlay:
            self.orig_w = self._w
        self._w = Overlay(top_w=overlay_widget,
                          bottom_w=self._w,
                          align='center',
                          width=('relative', 60),
                          min_width=80,
                          valign='middle',
                          height='pack')
        self.showing_overlay = True

    def remove_overlay(self, overlay_widget):
        # urwid note: we could also get orig_w as
        # self._w.contents[0][0], but this is clearer:
        self._w = self.orig_w
        self.showing_overlay = False
