#!/usr/bin/env python
#
# tests controllers/showsteps/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import ANY, call, MagicMock, patch, sentinel
from unittest.mock import MagicMock, patch, sentinel

from conjureup.controllers.showsteps.gui import ShowStepsController


class ShowStepsGUITestCase(unittest.TestCase):

    def setUp(self):

        self.controllers_patcher = patch(
            'conjureup.controllers.showsteps.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.showsteps.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.common_patcher = patch(
            'conjureup.controllers.showsteps.gui.common')
        self.mock_common = self.common_patcher.start()
        m_f = self.mock_common.get_step_metadata_filenames
        m_f.return_value = sentinel.step_metas

        self.view_patcher = patch(
            'conjureup.controllers.showsteps.gui.ShowStepsView')
        self.mock_view = self.view_patcher.start()

        self.controller = ShowStepsController()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.app_patcher.stop()
        self.common_patcher.stop()
        self.view_patcher.start()

    def test_render(self):
        "call next_step"
        self.controller.results = sentinel.results

        self.mock_app.steps = []
        self.controller.render()
        self.mock_controllers.use.assert_called_once_with('deploy')
        assert not self.mock_app.loop.create_task.called

        self.mock_app.steps = ['one']
        self.controller.render()
        assert self.mock_app.loop.create_task.called
