#!/usr/bin/env python
#
# tests controllers/deploy/gui.py
#
# Copyright 2016 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import unittest
from unittest.mock import ANY, call, patch, MagicMock
from conjure import juju

from conjure.controllers.deploy.gui import DeployController


class DeployGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        self.controller = DeployController()

        self.bundleinfo_patcher = patch(
            'conjure.controllers.deploy.gui.get_bundleinfo')
        self.mock_get_bundleinfo = self.bundleinfo_patcher.start()
        self.mock_bundle = MagicMock(name="bundle")
        self.mock_service_1 = MagicMock(name="s1")
        self.mock_get_bundleinfo.return_value = ("filename",
                                                 self.mock_bundle,
                                                 [self.mock_service_1])
        self.finish_patcher = patch(
            'conjure.controllers.deploy.gui.DeployController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.submit_patcher = patch(
            'conjure.controllers.deploy.gui.async.submit')
        self.mock_submit = self.submit_patcher.start()

        self.predeploy_call = call(self.controller._pre_deploy_exec, ANY,
                                   queue_name=juju.JUJU_ASYNC_QUEUE)
        self.add_machines_call = call(self.controller._do_add_machines, ANY,
                                      queue_name=juju.JUJU_ASYNC_QUEUE)

        self.view_patcher = patch(
            'conjure.controllers.deploy.gui.ServiceWalkthroughView')
        self.view_patcher.start()
        self.ui_patcher = patch(
            'conjure.controllers.deploy.gui.app')
        mock_app = self.ui_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")

    def tearDown(self):
        self.bundleinfo_patcher.stop()
        self.finish_patcher.stop()
        self.submit_patcher.stop()
        self.view_patcher.stop()
        self.ui_patcher.stop()

    def test_queue_predeploy_skipping(self):
        "Test that we do not call predeploy more than once"

        self.controller.is_predeploy_queued = True
        self.controller.render()

        self.mock_submit.assert_called_once_with(
            self.controller._do_add_machines, ANY,
            queue_name=juju.JUJU_ASYNC_QUEUE)

    def test_queue_predeploy_once(self):
        "Call submit to schedule predeploy if we haven't yet"
        self.controller.render()
        self.mock_submit.assert_has_calls([self.predeploy_call,
                                           self.add_machines_call],
                                          any_order=True)

    def test_call_add_machines_once_only(self):
        "Call add_machines once"
        self.controller.render()
        self.mock_submit.assert_has_calls([self.predeploy_call,
                                           self.add_machines_call],
                                          any_order=True)

        self.mock_submit.reset_mock()
        self.controller.is_predeploy_queued = True
        self.controller.render()
        self.assertEqual(self.mock_submit.call_count, 0)

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
