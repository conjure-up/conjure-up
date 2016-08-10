#!/usr/bin/env python
#
# tests controllers/clouds/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest

from unittest.mock import call, patch, MagicMock

from conjureup.controllers.clouds.gui import CloudsController


class CloudsGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = CloudsController()

        self.utils_patcher = patch(
            'conjureup.controllers.clouds.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.clouds.gui.CloudsController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.clouds.gui.CloudView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.clouds.gui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")
        self.list_clouds_patcher = patch(
            'conjureup.controllers.clouds.gui.list_clouds')
        self.mock_list_clouds = self.list_clouds_patcher.start()
        self.mock_list_clouds.return_value = ['test1', 'test2']

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.list_clouds_patcher.start()

    def test_render(self):
        "call render"
        self.controller.render()


class CloudsGUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = CloudsController()

        self.controllers_patcher = patch(
            'conjureup.controllers.clouds.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.clouds.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.clouds.gui.CloudsController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.clouds.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.cloudname = 'testcloudname'
        self.juju_patcher = patch(
            'conjureup.controllers.clouds.gui.juju')
        self.mock_juju = self.juju_patcher.start()

        self.gcc_patcher = patch(
            'conjureup.controllers.clouds.gui.get_controller_in_cloud')
        self.mock_gcc = self.gcc_patcher.start()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.juju_patcher.stop()
        self.gcc_patcher.stop()

    def test_finish_w_controller(self):
        "clouds.finish with an existing controller"
        self.mock_gcc.return_value = 'testcontroller'
        self.controller.finish('testcloud')
        self.mock_juju.assert_has_calls([
            call.switch_controller('testcontroller')])

    def test_finish_no_controller(self):
        "clouds.finish without existing controller"
        self.mock_gcc.return_value = None
        self.controller.finish('testcloud')
        self.mock_controllers.use.assert_has_calls([
            call('newcloud'), call().render('testcloud')])
