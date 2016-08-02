#!/usr/bin/env python
#
# tests controllers/clouds/tui.py
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
#  from unittest.mock import ANY, call, MagicMock, patch, sentinel
from unittest.mock import patch, MagicMock

from conjureup.controllers.clouds.tui import CloudsController


class CloudsTUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = CloudsController()

        self.utils_patcher = patch(
            'conjureup.controllers.clouds.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.clouds.tui.CloudsController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.clouds.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.juju_patcher = patch(
            'conjureup.controllers.clouds.tui.juju')
        self.mock_juju = self.juju_patcher.start()

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.app_patcher.stop()
        self.juju_patcher.stop()

    def test_render(self):
        "Rendering with a known cloud should call finish"
        self.mock_app.argv.cloud = "testcloud"
        t = ['testcloud']
        self.mock_juju.get_clouds.return_value.keys.return_value = t
        self.controller.render()
        self.mock_finish.assert_called_once_with()

    def test_render_unknown(self):
        "Rendering with an unknown cloud should raise"
        with self.assertRaises(SystemExit):
            self.controller.render()


class CloudsTUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = CloudsController()

        self.controllers_patcher = patch(
            'conjureup.controllers.clouds.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.clouds.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.clouds.tui.CloudsController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.clouds.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()

    def test_finish(self):
        "call finish"
        self.controller.finish()
