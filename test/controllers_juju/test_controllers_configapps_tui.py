#!/usr/bin/env python
#
# tests controllers/deploy/tui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import , call, MagicMock, patch, sentinel
from unittest.mock import MagicMock, call, patch, sentinel

from conjureup.controllers.juju.deploy.tui import DeployController


class DeployTUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.common_patcher = patch(
            'conjureup.controllers.juju.deploy.tui.common')
        self.mock_common = self.common_patcher.start()
        self.mock_common.do_deploy.return_value = sentinel.do_deploy

        self.controllers_patcher = patch(
            'conjureup.controllers.juju.deploy.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.juju.deploy.tui.app')
        self.mock_app = self.app_patcher.start()

        self.controller = DeployController()
        self.controller._wait_for_applications = MagicMock(
            return_value=sentinel.wait)

    def tearDown(self):
        self.common_patcher.stop()
        self.controllers_patcher.stop()
        self.app_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()
        assert self.mock_app.loop.create_task.called
        self.assertEqual(self.mock_app.loop.create_task.mock_calls, [
            call(sentinel.do_deploy),
            call(sentinel.wait)])
