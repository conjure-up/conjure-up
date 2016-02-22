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

import logging
from subprocess import Popen, PIPE, TimeoutExpired

from urwid import (AttrMap, Button, Columns, Divider, Filler, Overlay,
                   GridFlow, Frame, Padding, Pile, Text, WidgetWrap)

from ubuntui.views import InfoDialogWidget
from ubuntui.widgets import MetaScroll

from bundleplacer.ui.filter_box import FilterBox
from bundleplacer.ui.services_column import ServicesColumn
from bundleplacer.ui.machines_column import MachinesColumn
from bundleplacer.ui.machine_chooser import MachineChooser
from bundleplacer.ui.service_chooser import ServiceChooser


log = logging.getLogger('bundleplacer')


BUTTON_SIZE = 20


class PlacementView(WidgetWrap):

    """
    Handles display of machines and services.

    displays nothing if self.controller is not set.
    set it to a PlacementController.

    :param do_deploy_cb: deploy callback from controller
    """

    def __init__(self, display_controller, placement_controller,
                 config, do_deploy_cb):
        self.display_controller = display_controller
        self.placement_controller = placement_controller
        self.config = config
        self.do_deploy_cb = do_deploy_cb

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
            self.focus_machines_column()

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
        self.clear_all_button = AttrMap(Button("Clear All Placements",
                                               on_press=self.do_clear_all),
                                        'button_secondary',
                                        'button_secondary focus')

        self.services_buttons = [self.clear_all_button]
        self.services_button_grid = GridFlow(self.services_buttons,
                                             36, 1, 0, 'center')

        self.services_header_pile = Pile([Text(("body", "Services"),
                                               align='center'),
                                          Divider(),
                                          self.services_button_grid])
        return self.services_header_pile

    def get_machines_header(self, machines_column):

        self.open_maas_button = AttrMap(Button("Open in Browser",
                                               on_press=self.browse_maas),
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

    def build_widgets(self):

        self.services_column = ServicesColumn(self.display_controller,
                                              self.placement_controller,
                                              self)

        self.machines_column = MachinesColumn(self.display_controller,
                                              self.placement_controller,
                                              self)

        cs = [self.get_services_header(),
              self.get_machines_header(self.machines_column)]
        self.header_columns = Columns(cs)

        self.columns = Columns([self.services_column,
                                self.machines_column])

        self.deploy_button = Button("Deploy", on_press=self.do_deploy)
        self.deploy_button_label = Text("Some charms use default")
        self.main_pile = Pile([Padding(self.columns,
                                       align='center',
                                       width=('relative', 95))])
        b = AttrMap(self.deploy_button,
                    'button_primary',
                    'button_primary focus')
        self.frame = Frame(header=self.header_columns,
                           body=Filler(self.main_pile, valign='top'),
                           footer=GridFlow([self.deploy_button_label,
                                            b], 22, 1, 1, 'right'))
        return self.frame

    def update(self):
        self.services_column.update()
        self.machines_column.update()

        unplaced = self.placement_controller.unassigned_undeployed_services()
        all = self.placement_controller.charm_classes()
        n_total = len(all)
        remaining = len(unplaced) + len([c for c in all if c.subordinate])
        dmsg = "Deploy (Auto-assigning {}/{} charms)".format(remaining,
                                                             n_total)
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

    def do_clear_machine(self, sender, machine):
        self.placement_controller.clear_assignments(machine)

    def reset_selections(self, top=False):
        self.services_column.clear_selections()
        self.machines_column.clear_selections()
        self.update()
        self.columns.focus_position = 0

        if top:
            self.services_column.focus_top()
        else:
            self.services_column.focus_next()

    def focus_machines_column(self):
        self.columns.focus_position = 1
        self.machines_column.focus_prev_or_top()

    def do_show_service_chooser(self, sender, machine):
        self.show_overlay(ServiceChooser(self.placement_controller,
                                         machine,
                                         self))

    def do_deploy(self, sender):
        self.do_deploy_cb()

    def do_show_machine_chooser(self, sender, charm_class):
        self.show_overlay(MachineChooser(self.placement_controller,
                                         charm_class,
                                         self))

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
