#!/usr/bin/env python
#
# tests controllers/newcloud/tui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
#  from unittest.mock import ANY, call, MagicMock, patch
from unittest.mock import patch, MagicMock, sentinel

from conjureup.controllers.newcloud.tui import NewCloudController


class NewCloudTUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = NewCloudController()
        self.controller.do_post_bootstrap = MagicMock()

        self.utils_patcher = patch(
            'conjureup.controllers.newcloud.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.finish_patcher = patch(
            'conjureup.controllers.newcloud.tui.NewCloudController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.newcloud.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.juju_patcher = patch(
            'conjureup.controllers.newcloud.tui.juju')
        self.mock_juju = self.juju_patcher.start()

        self.common_patcher = patch(
            'conjureup.controllers.newcloud.tui.common')
        self.mock_common = self.common_patcher.start()

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.app_patcher.stop()
        self.mock_juju.stop()
        self.common_patcher.stop()

    def test_render_non_localhost_no_creds(self):
        "non-localhost cloud raises if no creds"
        self.mock_common.try_get_creds.return_value = False
        with self.assertRaises(SystemExit):
            self.controller.render('testcloud')

    def test_render_non_localhost_with_creds(self):
        "non-localhost cloud ok if has creds"
        self.mock_common.try_get_creds.return_value = True
        self.controller.render('testcloud')
        print(self.mock_common.mock_calls)

    def test_render(self):
        self.mock_common.try_get_creds.return_value = True
        self.mock_app.current_controller = sentinel.controllername
        self.controller.render('localhost')
        self.mock_juju.bootstrap.assert_called_once_with(
            controller=sentinel.controllername,
            cloud='localhost',
            credential=True)

        self.controller.do_post_bootstrap.assert_called_once_with()
        self.mock_finish.assert_called_once_with()


class NewCloudTUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = NewCloudController()

        self.controllers_patcher = patch(
            'conjureup.controllers.newcloud.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.newcloud.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.newcloud.tui.NewCloudController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.newcloud.tui.app')
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
