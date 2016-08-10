#!/usr/bin/env python
#
# tests controllers/steps/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import ANY, call, MagicMock, patch, sentinel
from unittest.mock import patch, MagicMock, sentinel

from conjureup.controllers.steps.gui import StepsController


class StepsGUIRenderTestCase(unittest.TestCase):
    def setUp(self):

        self.utils_patcher = patch(
            'conjureup.controllers.steps.gui.utils')
        self.mock_utils = self.utils_patcher.start()

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

        self.controller = StepsController()

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.common_patcher.stop()

    def test_render(self):
        "call render"
        self.mock_common.get_step_metadata_filenames.return_value = []
        self.controller.render()


class StepsGUIFinishTestCase(unittest.TestCase):
    def setUp(self):

        self.controllers_patcher = patch(
            'conjureup.controllers.steps.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.steps.gui.utils')
        self.mock_utils = self.utils_patcher.start()

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

        self.submit_patcher = patch(
            'conjureup.controllers.steps.gui.async.submit')
        self.mock_submit = self.submit_patcher.start()

        self.controller = StepsController()
        self.mock_stepsview = MagicMock()
        self.controller.view = self.mock_stepsview

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.common_patcher.stop()
        self.submit_patcher.stop()

    def test_finish_done(self):
        "call finish with done=True"
        self.controller.results = sentinel.results
        mock_model = MagicMock(name="model")
        mock_widget = MagicMock(name="widget")
        self.controller.finish(mock_model, mock_widget, done=True)
        m_r = self.mock_controllers.use('summary').render
        m_r.assert_called_once_with(sentinel.results)
