#!/usr/bin/env python
#
# tests controllers/summary/gui.py
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

from unittest.mock import call, patch, MagicMock, sentinel

from conjureup.controllers.summary.gui import SummaryController


class SummaryGUIRenderTestCase(unittest.TestCase):
    def setUp(self):

        self.finish_patcher = patch(
            'conjureup.controllers.summary.gui.SummaryController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.summary.gui.SummaryView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.summary.gui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")

        self.controller = SummaryController()
        self.controller.save_path = sentinel.savepath

    def tearDown(self):
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()

    def test_render_empty(self):
        "call render with no results"
        with patch("conjureup.controllers.summary.gui.common") as m_c:
            self.controller.render({})
            m_c.write_results.assert_called_once_with({}, sentinel.savepath)


class SummaryGUIFinishTestCase(unittest.TestCase):
    def setUp(self):

        self.render_patcher = patch(
            'conjureup.controllers.summary.gui.SummaryController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.summary.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.controller = SummaryController()

    def tearDown(self):
        self.render_patcher.stop()
        self.app_patcher.stop()

    def test_finish(self):
        "finish should stop event loop"
        with patch("conjureup.controllers.summary.gui.EventLoop") as m_ev:
            self.controller.finish()
            m_ev.assert_has_calls([call.remove_alarms(), call.exit(0)])
