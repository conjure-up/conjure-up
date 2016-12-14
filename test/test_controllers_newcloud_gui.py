#!/usr/bin/env python
#
# tests controllers/newcloud/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import ANY, call, MagicMock, patch, sentinel
from unittest.mock import MagicMock, patch

from conjureup.controllers.newcloud.gui import NewCloudController


class NewCloudGUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = NewCloudController()

        self.utils_patcher = patch(
            'conjureup.controllers.newcloud.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.newcloud.gui.NewCloudController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.newcloud.gui.NewCloudView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.newcloud.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.track_screen_patcher = patch(
            'conjureup.controllers.newcloud.gui.track_screen')
        self.mock_track_screen = self.track_screen_patcher.start()

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.track_screen_patcher.stop()

    def test_render(self):
        "call render"
        self.mock_app.current_cloud = 'maas'
        self.controller.render()


class NewCloudGUIFinishTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = NewCloudController()

        self.controllers_patcher = patch(
            'conjureup.controllers.newcloud.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.newcloud.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.newcloud.gui.NewCloudController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.newcloud.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.track_screen_patcher = patch(
            'conjureup.controllers.newcloud.gui.track_screen')
        self.mock_track_screen = self.track_screen_patcher.start()
        self.track_event_patcher = patch(
            'conjureup.controllers.newcloud.gui.track_event')
        self.mock_track_event = self.track_event_patcher.start()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.track_screen_patcher.stop()
        self.track_event_patcher.stop()

    def test_finish(self):
        "call finish"
        self.controller.finish()
