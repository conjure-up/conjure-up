#!/usr/bin/env python
#
# tests controllers/deploystatus/gui.py
#
# Copyright 2016, 2017 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, patch

from conjureup.controllers.deploystatus.gui import DeployStatusController


class DeployStatusGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.view_patcher = patch(
            'conjureup.controllers.deploystatus.gui.DeployStatusView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.deploystatus.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.controller = DeployStatusController()
        self.track_screen_patcher = patch(
            'conjureup.controllers.deploystatus.gui.track_screen')
        self.mock_track_screen = self.track_screen_patcher.start()
        self.controller._wait_for_applications = MagicMock()
        self.controller._refresh = MagicMock()

    def tearDown(self):
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.track_screen_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()
        assert self.mock_app.loop.create_task.called
