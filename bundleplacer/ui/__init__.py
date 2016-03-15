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
from subprocess import Popen, PIPE, TimeoutExpired

from urwid import (AttrMap, Columns, Divider, Filler, Overlay,
                   GridFlow, Frame, Padding, Pile, Text, WidgetWrap)

from ubuntui.widgets.buttons import PlainButton, MenuSelectButton
from ubuntui.views import InfoDialogWidget
from ubuntui.widgets import MetaScroll

from bundleplacer.ui.charmstore import CharmstoreColumn, CharmStoreSearchWidget
from bundleplacer.ui.filter_box import FilterBox
from bundleplacer.ui.services_column import ServicesColumn
from bundleplacer.ui.machines_column import MachinesColumn
from bundleplacer.ui.relations_column import RelationsColumn

log = logging.getLogger('bundleplacer')


BUTTON_SIZE = 20


class UIState(Enum):
    PLACEMENT_EDITOR = 0
    RELATION_EDITOR = 1
    CHARMSTORE_VIEW = 2         # This is the default


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
        self.prev_state = None
        w = self.build_widgets()
        super().__init__(w)
        self.reset_selections(top=True)  # calls self.update

    def scroll_down(self):
        pass

    def scroll_up(self):
        pass

    def focus_footer(self):
        self.frame.focus_position = 'footer'
        self.frame.footer.focus_position = 1

    def handle_tab(self, backward):
        if self.state == UIState.RELATION_EDITOR:
            # Relation editor has no header col.
            tabloop = ['headercol1', 'col1', 'col2', 'footer']
        else:
            tabloop = ['headercol1', 'col1', 'headercol2', 'col2', 'footer']

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
        else:
            return self._w.keypress(size, key)

    def get_services_header(self):
        b = PlainButton("Clear All Placements",
                        on_press=self.do_clear_all)
        self.clear_all_button = AttrMap(b,
                                        'button_secondary',
                                        'button_secondary focus')

        self.services_buttons = [self.clear_all_button]
        self.services_button_grid = GridFlow(self.services_buttons,
                                             36, 1, 0, 'center')

        self.services_header_pile = Pile([Text(("bobdy", "Services"),
                                               align='center'),
                                          Divider(),
                                          self.services_button_grid])

        return self.services_header_pile

    def get_charmstore_header(self, charmstore_column):
        self.charm_search_widget = CharmStoreSearchWidget(self.do_add_charm,
                                                          charmstore_column)
        self.charm_search_header_pile = Pile([Text(("bobdy", "Add Charms"),
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

        bc = self.config.juju_env['bootstrap-config']
        maasname = "'{}' <{}>".format(bc['name'], bc['maas-server'])
        maastitle = "Connected to MAAS {}".format(maasname)
        maastitle_grid = GridFlow([Text(maastitle), self.open_maas_button],
                                  22, 1, 1, 'center')

        f = machines_column.machines_list.handle_filter_change
        self.filter_edit_box = FilterBox(f)
        pl = [Text(('body',
                    "Ready Machines {}".format(MetaScroll().get_text()[0])),
                   align='center'),
              Divider(),
              maastitle_grid,
              Divider(),
              self.filter_edit_box]

        self.machines_header_pile = Pile(pl)
        return self.machines_header_pile

    def get_relations_header(self):
        return Text("Relation Editor")

    def build_widgets(self):

        self.services_column = ServicesColumn(self.display_controller,
                                              self.placement_controller,
                                              self)

        self.machines_column = MachinesColumn(self.display_controller,
                                              self.placement_controller,
                                              self)
        self.relations_column = RelationsColumn(self.display_controller,
                                                self.placement_controller,
                                                self)
        self.charmstore_column = CharmstoreColumn(self.display_controller,
                                                  self.placement_controller,
                                                  self)

        self.machines_header = self.get_machines_header(self.machines_column)
        self.relations_header = self.get_relations_header()
        self.services_header = self.get_services_header()
        self.charmstore_header = self.get_charmstore_header(
            self.charmstore_column)

        cs = [self.services_header, self.charmstore_header]

        self.header_columns = Columns(cs, dividechars=2)

        self.columns = Columns([self.services_column,
                                self.machines_column], dividechars=2)

        self.deploy_button = MenuSelectButton("\nDeploy\n",
                                              on_press=self.do_deploy)
        self.deploy_button_label = Text("Some charms use default")
        self.placement_edit_body = Filler(Padding(self.columns,
                                                  align='center',
                                                  width=('relative', 95)),
                                          valign='top')
        b = AttrMap(self.deploy_button,
                    'frame_header',
                    'button_primary focus')

        self.frame = Frame(header=self.header_columns,
                           body=self.placement_edit_body,
                           footer=GridFlow([self.deploy_button_label,
                                            b], 22, 1, 1, 'right'))
        return self.frame

    def update(self):
        if self.prev_state != self.state:
            h_opts = self.header_columns.options()
            c_opts = self.columns.options()
            
            if self.state == UIState.PLACEMENT_EDITOR:
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

            self.prev_state = self.state

        self.services_column.update()

        if self.state == UIState.PLACEMENT_EDITOR:
            self.machines_column.update()
        elif self.state == UIState.RELATION_EDITOR:
            self.relations_column.update()

        self.charm_search_widget.update()

        unplaced = self.placement_controller.unassigned_undeployed_services()
        all = self.placement_controller.services()
        n_subs = len([c for c in all if c.subordinate])
        n_total = len(all) - n_subs
        remaining = len(unplaced) - n_subs
        if remaining > 0:
            dmsg = "Auto-assigning {}/{} charms".format(remaining,
                                                                  n_total)
        else:
            dmsg = ""
        self.deploy_button_label.set_text(dmsg)

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
        service_name = self.placement_controller.add_new_service(charm_name,
                                                                 charm_dict)
        self.frame.focus_position = 'body'
        self.columns.focus_position = 0
        self.relations_column.add_charm(charm_name)
        self.update()
        self.services_column.select_service(service_name)

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

    def focus_charmstore_column(self):
        self.columns.focus_position = 1
        self.charmstore_column.focus_prev_or_top()

    def edit_placement(self):
        self.state = UIState.PLACEMENT_EDITOR
        self.update()
        self.focus_machines_column()

    def show_default_view(self):
        self.state = UIState.CHARMSTORE_VIEW
        self.update()

    def edit_relations(self, service):
        self.state = UIState.RELATION_EDITOR
        self.relations_column.set_service(service)
        self.update()
        self.focus_relations_column()

    def do_deploy(self, sender):
        self.do_deploy_cb()

    def show_overlay(self, overlay_widget):
        self.orig_w = self._w
        self._w = Overlay(top_w=overlay_widget,
                          bottom_w=self._w,
                          align='center',
                          width=('relative', 60),
                          min_width=80,
                          valign='middle',
                          height='pack')

    def remove_overlay(self, overlay_widget):
        # urwid note: we could also get orig_w as
        # self._w.contents[0][0], but this is clearer:
        self._w = self.orig_w
