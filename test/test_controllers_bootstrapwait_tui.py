#!/usr/bin/env python
#
# tests controllers/bootstrapwait/tui.py
#
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


import unittest

from unittest.mock import patch

from conjureup.controllers.bootstrapwait.tui import BootstrapWaitController


class BootstrapwaitTUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = BootstrapWaitController()

        self.utils_patcher = patch(
            'conjureup.controllers.bootstrapwait.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.bootstrapwait.tui.'
            'BootstrapWaitController.finish')
        self.mock_finish = self.finish_patcher.start()

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()


class BootstrapwaitTUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = BootstrapWaitController()

        self.controllers_patcher = patch(
            'conjureup.controllers.bootstrapwait.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.bootstrapwait.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.bootstrapwait.tui.'
            'BootstrapWaitController.render')
        self.mock_render = self.render_patcher.start()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()

    def test_finish(self):
        "call finish"
        self.controller.finish()
