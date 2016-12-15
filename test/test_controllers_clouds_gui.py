#!/usr/bin/env python
#
# tests controllers/clouds/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, call, patch

from conjureup.controllers.clouds.gui import CloudsController


class CloudsGUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = CloudsController()

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

        self.track_screen_patcher = patch(
            'conjureup.controllers.clouds.gui.track_screen')
        self.mock_track_screen = self.track_screen_patcher.start()

    def tearDown(self):
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.list_clouds_patcher.stop()
        self.track_screen_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()


class CloudsGUIFinishTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = CloudsController()

        self.controllers_patcher = patch(
            'conjureup.controllers.clouds.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.clouds.gui.CloudsController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.clouds.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

        self.cloudname = 'testcloudname'

    def tearDown(self):
        self.controllers_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()

    def test_finish_no_controller(self):
        "clouds.finish without existing controller"
        self.controller.finish('testcloud')
        self.mock_controllers.use.assert_has_calls([
            call('newcloud'), call().render()])
