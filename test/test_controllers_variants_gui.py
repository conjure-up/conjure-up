#!/usr/bin/env python
#
# tests controllers/variants/gui.py
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

from conjureup.controllers.variants.gui import VariantsController


class VariantsGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = VariantsController()

        self.utils_patcher = patch(
            'conjureup.controllers.variants.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.variants.gui.VariantsController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.variants.gui.VariantView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.variants.gui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()


class VariantsGUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = VariantsController()

        self.controllers_patcher = patch(
            'conjureup.controllers.variants.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.variants.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.variants.gui.VariantsController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.variants.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.mock_spell = MagicMock(name='spell')

        self.download_patcher = patch(
            'conjureup.controllers.variants.gui.download')
        self.mock_download = self.download_patcher.start()

        self.get_remote_url_patcher = patch(
            'conjureup.controllers.variants.gui.get_remote_url')
        self.mock_get_remote_url = self.get_remote_url_patcher.start()

        self.json_patcher = patch(
            'conjureup.controllers.variants.gui.json')
        self.mock_json = self.json_patcher.start()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.download_patcher.stop()
        self.get_remote_url_patcher.stop()
        self.json_patcher.stop()

    def test_finish(self):
        "call finish in variants"
        self.controller.finish(self.mock_spell)
