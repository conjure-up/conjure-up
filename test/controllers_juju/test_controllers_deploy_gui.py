#!/usr/bin/env python
#
# tests controllers/deploy/gui.py
#
# Copyright 2016, 2017 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, patch

from conjureup.controllers.juju.deploy.gui import DeployController


class DeployGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.view_patcher = patch(
            'conjureup.controllers.juju.deploy.gui.DeployStatusView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.juju.deploy.gui.app')
        self.mock_app = self.app_patcher.start()

        self.controller = DeployController()
        self.controller._wait_for_applications = MagicMock()
        self.controller._refresh = MagicMock()
        self.common_patcher = patch(
            'conjureup.controllers.juju.deploy.gui.common')
        self.mock_common = self.common_patcher.start()

    def tearDown(self):
        self.common_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()
        assert self.mock_app.loop.create_task.called
