#!/usr/bin/env python
#
# tests controllers/deploy/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import ANY, MagicMock, call, patch, sentinel

from conjureup.controllers.deploy.gui import DeployController


class DeployGUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        with patch.object(DeployController, 'init_machines_assignments'):
            self.controller = DeployController()

        self.utils_patcher = patch(
            'conjureup.controllers.deploy.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.mock_bundle = MagicMock(name="bundle")
        self.mock_bundle.machines = {"1": sentinel.machine_1}
        self.mock_service_1 = MagicMock(name="s1")
        self.mock_bundle.services = [self.mock_service_1]
        self.finish_patcher = patch(
            'conjureup.controllers.deploy.gui.DeployController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.submit_patcher = patch(
            'conjureup.controllers.deploy.gui.async.submit')
        self.mock_submit = self.submit_patcher.start()

        self.predeploy_call = call(self.controller._pre_deploy_exec, ANY,
                                   queue_name=sentinel.JUJU_ASYNC_QUEUE)

        self.view_patcher = patch(
            'conjureup.controllers.deploy.gui.ApplicationListView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.deploy.gui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")
        mock_app.metadata_controller.bundle = self.mock_bundle
        mock_app.current_controller = 'testcontroller'
        mock_app.bootstrap.running.exception.return_value = None

        self.juju_patcher = patch(
            'conjureup.controllers.deploy.gui.juju')
        self.mock_juju = self.juju_patcher.start()
        self.mock_juju.JUJU_ASYNC_QUEUE = sentinel.JUJU_ASYNC_QUEUE

        self.track_screen_patcher = patch(
            'conjureup.controllers.deploy.gui.track_screen')
        self.mock_track_screen = self.track_screen_patcher.start()

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.submit_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.juju_patcher.stop()
        self.track_screen_patcher.stop()

    def test_queue_predeploy_once(self):
        "Call submit to schedule predeploy if we haven't yet"
        self.controller.render()
        self.mock_submit.assert_has_calls([self.predeploy_call],
                                          any_order=True)


class DeployGUIFinishTestCase(unittest.TestCase):

    def setUp(self):
        with patch.object(DeployController, 'init_machines_assignments'):
            self.controller = DeployController()

        self.controllers_patcher = patch(
            'conjureup.controllers.deploy.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.deploy.gui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.submit_patcher = patch(
            'conjureup.controllers.deploy.gui.async.submit')
        self.mock_submit = self.submit_patcher.start()
        self.mock_submit.return_value = sentinel.a_future

        self.juju_patcher = patch(
            'conjureup.controllers.deploy.gui.juju')
        self.mock_juju = self.juju_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.deploy.gui.DeployController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.deploy.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.submit_patcher.stop()
        self.juju_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()

    def test_show_bootstrap_wait(self):
        "Go to bootstrap wait controller if bootstrap pending"
        self.mock_app.bootstrap = MagicMock(name="bootstrap")
        self.mock_app.bootstrap.running = MagicMock(name='running_future')
        self.mock_app.bootstrap.running.done = MagicMock(name='done')
        self.mock_app.bootstrap.running.done.return_value = False
        self.controller.finish()
        self.assertEqual(1, len(self.mock_submit.mock_calls))
        self.assertEqual(self.mock_controllers.mock_calls,
                         [call.use('bootstrapwait'),
                          call.use().render(sentinel.a_future)])

    def test_skip_bootstrap_wait(self):
        "Go directly to deploystatus if bootstrap is done"
        self.controller.finish()
        self.assertEqual(1, len(self.mock_submit.mock_calls))
        self.assertEqual(self.mock_controllers.mock_calls,
                         [call.use('deploystatus'),
                          call.use().render(ANY)])
