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

from urwid import Divider, Pile, WidgetWrap

from bundleplacer.ui.services_list import ServicesList
from bundleplacer.ui.simple_service_widget import ServiceWidgetState

log = logging.getLogger('bundleplacer')


class ServicesColumn(WidgetWrap):

    """Displays dynamic list of unplaced services and associated controls
    """

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
        self.services_list = ServicesList(self.placement_controller,
                                          self.display_controller,
                                          title=None)

        self.services_pile = Pile([self.services_list, Divider()])

        return self.services_pile

    def focus_top(self):
        self.update()
        self.services_list.focus_top()

    def focus_next(self):
        self.update()
        moved = self.services_list.focus_top_or_next()
        fsw = self.services_list.focused_service_widget()
        if not moved or (fsw and fsw.service.subordinate):
            self.placement_view.focus_footer()

    def update(self):
        self.services_list.update()

    def do_reset_to_defaults(self, sender):
        self.placement_controller.set_all_assignments(
            self.placement_controller.gen_defaults())

    def clear_selections(self):
        for sw in self.services_list.service_widgets:
            sw.state = ServiceWidgetState.UNSELECTED

    def select_service(self, service_name):
        self.services_list.select_service(service_name)
