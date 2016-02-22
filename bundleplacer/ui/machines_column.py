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

from urwid import Divider, Pile, Text, WidgetWrap

from bundleplacer.ui.machines_list import MachinesList


log = logging.getLogger('bundleplacer')


BUTTON_SIZE = 20


class MachinesColumn(WidgetWrap):

    """Shows machines or a link to MAAS to add more"""

    def __init__(self, display_controller, placement_controller,
                 placement_view):
        self.display_controller = display_controller
        self.placement_controller = placement_controller
        self.placement_view = placement_view
        w = self.build_widgets()
        super().__init__(w)
        self.update()

    def selectable(self):
        return True

    def build_widgets(self):
        togglefunc = self.display_controller.do_toggle_selected_machine
        self.machines_list = MachinesList(self.placement_controller,
                                          self.display_controller,
                                          togglefunc,
                                          show_hardware=True,
                                          show_assignments=False,
                                          show_placeholders=False,
                                          show_only_ready=True,
                                          title_widgets=[])

        self.machines_list.update()

        self.machines_list_pile = Pile([self.machines_list,
                                        Divider()])

        return self.machines_list_pile

    def update(self):
        self.machines_list.update()
        bc = self.placement_view.config.juju_env['bootstrap-config']
        empty_maas_msg = ("There are no available machines.\n"
                          "Open {} to add machines to "
                          "'{}':".format(bc['maas-server'], bc['name']))

        self.empty_maas_widgets = Pile([Text([('error_icon',
                                               "\N{WARNING SIGN} "),
                                              empty_maas_msg],
                                             align='center')])

        # 2 machines is the subordinate placeholder + juju default:
        opts = self.machines_list_pile.options()
        if len(self.placement_controller.machines()) == 2:
            self.machines_list_pile.contents[0] = (self.empty_maas_widgets,
                                                   opts)
        else:
            self.machines_list_pile.contents[0] = (self.machines_list,
                                                   opts)

    def clear_selections(self):
        for mw in self.machines_list.machine_widgets:
            mw.is_selected = False

    def focus_prev_or_top(self):
        self.update()
        try:
            self.machines_list_pile.focus_position = 0
            self.machines_list.focus_prev_or_top()
        except IndexError:
            log.debug("caught indexerror in machinesColumn focus_prev_or_top")
            pass
