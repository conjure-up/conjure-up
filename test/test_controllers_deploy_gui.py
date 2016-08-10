#!/usr/bin/env python
#
# tests controllers/deploy/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import ANY, call, MagicMock, patch, sentinel

from conjureup.controllers.deploy.gui import DeployController


class DeployGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
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
            'conjureup.controllers.deploy.gui.ServiceWalkthroughView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.deploy.gui.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")
        mock_app.metadata_controller.bundle = self.mock_bundle

        self.juju_patcher = patch(
            'conjureup.controllers.deploy.gui.juju')
        self.mock_juju = self.juju_patcher.start()
        self.mock_juju.JUJU_ASYNC_QUEUE = sentinel.JUJU_ASYNC_QUEUE

    def tearDown(self):
        self.utils_patcher.stop()
        self.finish_patcher.stop()
        self.submit_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.juju_patcher.stop()

    def test_queue_predeploy_skipping(self):
        "Do not enqueue predeploy more than once"

        self.controller.is_predeploy_queued = True
        self.controller.render()
        self.assertEqual(self.mock_submit.call_count, 0)

    def test_queue_predeploy_once(self):
        "Call submit to schedule predeploy if we haven't yet"
        self.controller.render()
        self.mock_submit.assert_has_calls([self.predeploy_call],
                                          any_order=True)

    def test_call_add_machines_once_only(self):
        "Call add_machines once"
        self.controller.render()
        self.mock_submit.assert_has_calls([self.predeploy_call],
                                          any_order=True)

        self.mock_submit.reset_mock()
        self.controller.is_predeploy_queued = True
        self.controller.render()
        self.assertEqual(self.mock_submit.call_count, 0)
        self.mock_juju.add_machines.assert_called_once_with(
            [sentinel.machine_1], exc_cb=ANY)

    def test_finish_at_end(self):
        "Call finish only at end"
        # the ServiceWalkthroughView will call finish() for the first
        # N-1 services if the user chooses to do so individually

        self.assertEqual(self.mock_finish.call_count, 0)
        self.controller.render()
        self.assertEqual(self.mock_finish.call_count, 0)
        self.controller.svc_idx += 1
        self.controller.render()
        self.mock_finish.assert_called_once_with()


class DeployGUIFinishTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = DeployController()

        self.controllers_patcher = patch(
            'conjureup.controllers.deploy.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.deploy.gui.utils')
        self.mock_utils = self.utils_patcher.start()

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
        self.juju_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()

    def test_deploy_single(self):
        "Deploy a single service in finish"
        self.controller.finish(sentinel.single_service)
        self.assertEqual(self.mock_juju.mock_calls,
                         [call.deploy_service(sentinel.single_service,
                                              ANY, ANY)])
        self.mock_render.assert_called_once_with()
        self.assertEqual(self.mock_controllers.mock_calls, [])

    def test_deploy_rest(self):
        "Deploy multiple services in finish"
        self.controller.services = [sentinel.service_1, sentinel.service_2]
        self.controller.finish()
        self.assertEqual(self.mock_juju.mock_calls,
                         [call.deploy_service(sentinel.service_1, ANY, ANY),
                          call.deploy_service(sentinel.service_2, ANY, ANY),
                          call.set_relations([sentinel.service_1,
                                              sentinel.service_2], ANY, ANY)])

    def test_show_bootstrap_wait(self):
        "Go to bootstrap wait controller if bootstrap pending"
        self.mock_app.bootstrap = MagicMock(name="bootstrap")
        self.mock_app.bootstrap.running = MagicMock(name='running_future')
        self.mock_app.bootstrap.running.done = MagicMock(name='done')
        self.mock_app.bootstrap.running.done.return_value = False
        self.controller.finish()
        self.assertEqual(self.mock_controllers.mock_calls,
                         [call.use('bootstrapwait'),
                          call.use().render()])

    def test_skip_bootstrap_wait(self):
        "Go directly to deploystatus if bootstrap is done"
        self.controller.finish()
        self.assertEqual(self.mock_controllers.mock_calls,
                         [call.use('deploystatus'),
                          call.use().render()])
