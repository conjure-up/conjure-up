#!/usr/bin/env python
#
# tests controllers/lxdsetup/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import ANY, call, MagicMock, patch, sentinel
from unittest.mock import patch, MagicMock

from conjureup.controllers.lxdsetup.gui import LXDSetupController


class LXDSetupGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = LXDSetupController()

        self.utils_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.LXDSetupController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.LXDSetupView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.app')
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


class LXDSetupGUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = LXDSetupController()

        self.controllers_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.LXDSetupController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.app')
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
