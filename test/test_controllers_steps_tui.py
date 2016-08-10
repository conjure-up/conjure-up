#!/usr/bin/env python
#
# tests controllers/steps/tui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest

from unittest.mock import patch, MagicMock, sentinel

from conjureup.controllers.steps.tui import StepsController


class StepsTUIRenderTestCase(unittest.TestCase):
    def setUp(self):

        self.utils_patcher = patch(
            'conjureup.controllers.steps.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.steps.tui.StepsController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.steps.tui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")

        self.common_patcher = patch(
            'conjureup.controllers.steps.tui.common')
        self.mock_common = self.common_patcher.start()
        self.controller = StepsController()

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.app_patcher.stop()
        self.common_patcher.stop()

    def test_render(self):
        "call render"
        self.mock_common.get_step_metadata_filenames.return_value = []
        self.controller.render()


class StepsTUIFinishTestCase(unittest.TestCase):
    def setUp(self):

        self.controllers_patcher = patch(
            'conjureup.controllers.steps.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.steps.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.steps.tui.StepsController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.steps.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.common_patcher = patch(
            'conjureup.controllers.steps.tui.common')
        self.mock_common = self.common_patcher.start()
        m_f = self.mock_common.get_step_metadata_filenames
        m_f.return_value = sentinel.step_metas
        self.controller = StepsController()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.common_patcher.stop()

    def test_finish(self):
        "call finish"
        self.controller.finish()
