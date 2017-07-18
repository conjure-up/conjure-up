#!/usr/bin/env python
#
# tests controllers/deploy/tui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import , call, MagicMock, patch, sentinel
from unittest.mock import MagicMock, patch, sentinel

from conjureup.controllers.deploy.tui import DeployController

from .helpers import test_loop


class DeployTUIRenderTestCase(unittest.TestCase):

    def setUp(self):

        self.utils_patcher = patch(
            'conjureup.controllers.deploy.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.do_deploy_patcher = patch(
            'conjureup.controllers.deploy.tui.DeployController.do_deploy')
        self.mock_do_deploy = self.do_deploy_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.deploy.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.mock_bundle = MagicMock(name="bundle")
        self.mock_bundle.machines = {"1": sentinel.machine_1}
        self.mock_service_1 = MagicMock(name="s1")

        self.controller = DeployController()

        self.juju_patcher = patch(
            'conjureup.controllers.deploy.tui.juju')
        self.mock_juju = self.juju_patcher.start()

    def tearDown(self):
        self.utils_patcher.stop()
        self.do_deploy_patcher.stop()
        self.app_patcher.stop()
        self.juju_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()
        assert self.mock_app.loop.create_task.called


class DeployTUIDoDeployTestCase(unittest.TestCase):

    def setUp(self):
        async def dummy():
            pass

        self.controller = DeployController()

        self.controllers_patcher = patch(
            'conjureup.controllers.deploy.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.deploy.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.common_patcher = patch(
            'conjureup.controllers.deploy.tui.common')
        self.mock_common = self.common_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.deploy.tui.DeployController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.deploy.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.events_app_patcher = patch('conjureup.events.app', self.mock_app)
        self.events_app_patcher.start()
        self.juju_patcher = patch(
            'conjureup.controllers.deploy.tui.juju')
        self.mock_juju = self.juju_patcher.start()

        self.mock_common.pre_deploy.return_value = dummy()
        self.mock_juju.add_machines.return_value = dummy()
        self.mock_juju.deploy_service.return_value = dummy()
        self.mock_juju.add_model.return_value = dummy()
        self.mock_juju.set_relations.return_value = dummy()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.common_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.events_app_patcher.stop()
        self.juju_patcher.stop()

    def test_do_deploy(self):
        "call do_deploy"
        self.mock_app.metadata_controller.bundle.services = [
            MagicMock(service_name='service'),
        ]

        with test_loop() as loop:
            loop.run_until_complete(self.controller.do_deploy())

        assert self.mock_common.pre_deploy.called
        assert self.mock_juju.add_model.called
        assert self.mock_juju.add_machines.called
        assert self.mock_juju.deploy_service.called
        assert self.mock_juju.set_relations.called
        self.mock_controllers.use.assert_called_with('deploystatus')
