#!/usr/bin/env python
#
# tests controllers/clouds/tui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, call, patch

from conjureup import events
from conjureup.controllers.juju.clouds.tui import CloudsController


class CloudsTUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = CloudsController()

        self.utils_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.CloudsController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()

        self.juju_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.juju')
        self.mock_juju = self.juju_patcher.start()
        events.Shutdown.clear()

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()
        self.juju_patcher.stop()

    def test_render(self):
        "Rendering with a known cloud should call finish"
        self.controller._check_lxd_compat = MagicMock()
        self.mock_app.provider.cloud = "aws"
        t = ['aws']
        self.mock_juju.get_clouds.return_value.keys.return_value = t
        self.controller.render()
        assert self.mock_app.loop.create_task.called


class CloudsTUIFinishTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = CloudsController()

        self.controllers_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.CloudsController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.mock_app.conjurefile = {}
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()
        self.juju_patcher = patch(
            'conjureup.controllers.juju.clouds.tui.juju')
        self.mock_juju = self.juju_patcher.start()

        self.gcc_patcher = patch(
            'conjureup.controllers.juju.clouds.'
            'tui.juju.get_controller_in_cloud')
        self.mock_gcc = self.gcc_patcher.start()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()
        self.juju_patcher.stop()
        self.gcc_patcher.stop()

    def test_finish_w_model(self):
        "clouds.finish with an existing controller"
        self.mock_gcc.return_value = 'testcontroller'
        self.mock_app.conjurefile['model'] = 'testmodel'
        self.mock_app.provider.cloud = 'cloud'
        self.controller.finish()
        self.mock_controllers.use.assert_has_calls([
            call('credentials'), call().render()])

    def test_finish_no_model(self):
        "clouds.finish without existing controller"
        self.mock_gcc.return_value = None
        self.mock_app.conjurefile['cloud'] = 'testcloud'
        self.mock_app.conjurefile['controller'] = None
        self.mock_app.conjurefile['model'] = None
        self.controller.finish()
        self.mock_controllers.use.assert_has_calls([
            call('credentials'), call().render()])
