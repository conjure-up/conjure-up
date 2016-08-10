#!/usr/bin/env python
#
# tests controllers/deploy/tui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import , call, MagicMock, patch, sentinel
from unittest.mock import ANY, patch, MagicMock, sentinel

from conjureup.controllers.deploy.tui import DeployController


class DeployTUIRenderTestCase(unittest.TestCase):
    def setUp(self):

        self.utils_patcher = patch(
            'conjureup.controllers.deploy.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.deploy.tui.DeployController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.deploy.tui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")

        self.mock_bundle = MagicMock(name="bundle")
        self.mock_bundle.machines = {"1": sentinel.machine_1}
        self.mock_service_1 = MagicMock(name="s1")

        self.controller = DeployController()

        self.juju_patcher = patch(
            'conjureup.controllers.deploy.tui.juju')
        self.mock_juju = self.juju_patcher.start()
        self.mock_juju.JUJU_ASYNC_QUEUE = sentinel.JUJU_ASYNC_QUEUE

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.app_patcher.stop()
        self.juju_patcher.stop()

    def test_render(self):
        "call render"
        with patch.object(self.controller, 'do_pre_deploy') as mock_predeploy:
            self.controller.render()
            mock_predeploy.assert_called_once_with()
        self.mock_juju.add_machines.assert_called_once_with(ANY, exc_cb=ANY)


class DeployTUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = DeployController()

        self.controllers_patcher = patch(
            'conjureup.controllers.deploy.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.deploy.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.deploy.tui.DeployController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.deploy.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.juju_patcher = patch(
            'conjureup.controllers.deploy.tui.juju')
        self.mock_juju = self.juju_patcher.start()
        self.mock_juju.JUJU_ASYNC_QUEUE = sentinel.JUJU_ASYNC_QUEUE

        self.concurrent_patcher = patch(
            'conjureup.controllers.deploy.tui.concurrent')
        self.mock_concurrent = self.concurrent_patcher.start()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.juju_patcher.stop()
        self.concurrent_patcher.stop()

    def test_finish(self):
        "call finish"
        self.controller.finish()
