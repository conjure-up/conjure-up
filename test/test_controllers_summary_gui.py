#!/usr/bin/env python
#
# tests controllers/summary/gui.py
#
# Copyright 2016 Canonical, Ltd.


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
