#!/usr/bin/env python
#
# tests controllers/steps/tui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import patch

from conjureup.controllers.showsteps.tui import ShowStepsController


class StepsTUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.common_patcher = patch(
            'conjureup.controllers.showsteps.tui.common')
        self.mock_common = self.common_patcher.start()

        self.controllers_patcher = patch(
            'conjureup.controllers.showsteps.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()
        self.controller = ShowStepsController()

    def tearDown(self):
        self.common_patcher.stop()
        self.controllers_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()
        self.mock_common.load_steps.assert_called_once_with()
        self.mock_controllers.use.assert_called_once_with('deploy')
