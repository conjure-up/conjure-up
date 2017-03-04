#!/usr/bin/env python
#
# tests controllers/steps/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import ANY, call, MagicMock, patch, sentinel
from unittest.mock import MagicMock, patch, sentinel

from conjureup.controllers.steps.gui import StepsController


class StepsGUIRenderTestCase(unittest.TestCase):

    def setUp(self):

        self.finish_patcher = patch(
            'conjureup.controllers.steps.gui.StepsController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.steps.gui.StepsView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.steps.gui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")

        self.common_patcher = patch(
            'conjureup.controllers.steps.gui.common')
        self.mock_common = self.common_patcher.start()

        self.track_screen_patcher = patch(
            'conjureup.controllers.steps.gui.track_screen')
        self.mock_track_screen = self.track_screen_patcher.start()

        self.controller = StepsController()

    def tearDown(self):
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.common_patcher.stop()
        self.track_screen_patcher.stop()

    def test_render(self):
        "call render"
        self.mock_common.get_step_metadata_filenames.return_value = []
        self.controller.render()


class StepsGUIFinishTestCase(unittest.TestCase):

    def setUp(self):

        self.controllers_patcher = patch(
            'conjureup.controllers.steps.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.steps.gui.StepsController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.steps.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.common_patcher = patch(
            'conjureup.controllers.steps.gui.common')
        self.mock_common = self.common_patcher.start()
        m_f = self.mock_common.get_step_metadata_filenames
        m_f.return_value = sentinel.step_metas

        self.utils_patcher = patch(
            'conjureup.controllers.steps.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.controller = StepsController()
        self.mock_stepsview = MagicMock()
        self.controller.view = self.mock_stepsview
        self.controller._put = MagicMock()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.common_patcher.stop()

    def test_next_step(self):
        "call next_step"
        self.controller.results = sentinel.results
        mock_model = MagicMock(name="model")
        mock_widget = MagicMock(name="widget")
        self.controller.next_step(mock_model, mock_widget)
        assert self.mock_app.loop.create_task.called
