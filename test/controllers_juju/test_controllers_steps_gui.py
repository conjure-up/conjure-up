#!/usr/bin/env python
#
# tests controllers/showsteps/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import ANY, call, MagicMock, patch, sentinel
from unittest.mock import MagicMock, patch, sentinel

from conjureup.controllers.juju.showsteps.gui import ShowStepsController


class ShowStepsGUITestCase(unittest.TestCase):

    def setUp(self):

        self.controllers_patcher = patch(
            'conjureup.controllers.juju.showsteps.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.juju.showsteps.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.view_patcher = patch(
            'conjureup.controllers.juju.showsteps.gui.ShowStepsView')
        self.mock_view = self.view_patcher.start()

        self.controller = ShowStepsController()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.app_patcher.stop()
        self.view_patcher.start()

    def test_render(self):
        "call next_step"
        self.controller.results = sentinel.results
        self.controller.show_steps = MagicMock()

        self.mock_app.steps = []
        self.mock_app.has_bundle_modifications = False
        self.controller.render()
        self.mock_controllers.use.assert_called_once_with('configapps')
        assert not self.mock_app.loop.create_task.called

        self.mock_app.steps = ['one']
        self.controller.render()
        assert self.mock_app.loop.create_task.called
