#!/usr/bin/env python
#
# tests controllers/bundlereadme/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest

from unittest.mock import ANY, patch, MagicMock

from conjureup.controllers.bundlereadme.gui import BundleReadmeController


class BundleReadmeGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = BundleReadmeController()

        self.utils_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.'
            'BundleReadmeController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.BundleReadmeView')
        self.mock_view = self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")

        self.eventloop_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.EventLoop')
        self.mock_eventloop = self.eventloop_patcher.start()
        self.mock_eventloop.screen_size.return_value = (0, 100)

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.eventloop_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()
        self.mock_view.assert_called_once_with(ANY, ANY, 75)


class BundleReadmeGUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = BundleReadmeController()

        self.controllers_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.'
            'BundleReadmeController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.bundlereadme.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()

    def test_finish(self):
        "call finish"
        self.controller.finish()
        self.mock_controllers.use.assert_called_once_with('deploy')
