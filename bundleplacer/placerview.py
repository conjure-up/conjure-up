# -*- mode: python; -*-
#
# Copyright 2015 Canonical, Ltd.
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

from urwid import WidgetWrap

from bundleplacer.assignmenttype import AssignmentType
from bundleplacer.ui import PlacementView
from ubuntui.ev import EventLoop

log = logging.getLogger('bundleplacer')


class PlacerView(WidgetWrap):

    def __init__(self, placement_controller, config, cb,
                 has_maas=False):
        self.placement_controller = placement_controller
        self.config = config
        self.cb = cb
        self.has_maas = has_maas

        self.selected_machine = None
        self.selected_service = None
        self.pv = PlacementView(
            display_controller=self,
            placement_controller=self.placement_controller,
            config=self.config,
            do_deploy_cb=self.do_deploy,
            has_maas=has_maas)
        super().__init__(self.pv)
        self.pv.reset_selections(top=True)

    def update(self, *args, **kwargs):
        self.pv.update()
        EventLoop.set_alarm_in(1, self.update)

    def status_error_message(self, message):
        pass

    def status_info_message(self, message):
        pass

    def do_deploy(self):
        self.cb()

    def _do_select(self, machine, atype):
        self.placement_controller.assign(machine,
                                         self.selected_service,
                                         atype)
        self.pv.reset_selections()

    def do_select_baremetal(self, machine):
        self._do_select(machine, AssignmentType.BareMetal)

    def do_select_lxd(self, machine):
        self._do_select(machine, AssignmentType.LXD)

    def do_select_kvm(self, machine):
        self._do_select(machine, AssignmentType.KVM)

    def set_selected_service(self, service):
        self.selected_service = service

    def remove_service(self, service):
        self.placement_controller.remove_service(service.service_name)
        self.pv.update()

    def scale_service(self, service, amount):
        self.placement_controller.scale_service(service.service_name,
                                                amount)
        self.pv.update()

    def show_default_view(self):
        self.pv.show_default_view()

    def edit_placement(self):
        self.pv.edit_placement()

    def edit_relations(self):
        assert self.selected_service is not None
        self.pv.edit_relations(self.selected_service)

    def edit_options(self):
        assert self.selected_service is not None
        self.pv.edit_options(self.selected_service)

    def clear_selections(self):
        self.pv.clear_selections()
