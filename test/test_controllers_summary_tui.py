#!/usr/bin/env python
#
# tests controllers/summary/tui.py
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

from unittest.mock import patch, MagicMock, sentinel

from conjureup.controllers.summary.tui import SummaryController


class SummaryTUIRenderTestCase(unittest.TestCase):
    def setUp(self):

        self.utils_patcher = patch(
            'conjureup.controllers.summary.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.summary.tui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")
        self.controller = SummaryController()
        self.controller.save_path = sentinel.savepath

    def tearDown(self):
        self.utils_patcher.stop()
        self.app_patcher.stop()

    def test_render_empty(self):
        "call render with empty results"
        with patch("conjureup.controllers.summary.tui.common") as m_c:
            self.controller.render({})
            m_c.write_results.assert_called_once_with({}, sentinel.savepath)
