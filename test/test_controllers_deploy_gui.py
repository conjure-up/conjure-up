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
from unittest.mock import ANY, patch, MagicMock
from importlib import reload
from conjure import juju

import conjure.controllers.deploy.gui
guimodule = conjure.controllers.deploy.gui


class DeployGUIRenderTestCase(unittest.TestCase):
    def setUp(self):
        reload(conjure.controllers.deploy.gui)
        self.gui = conjure.controllers.deploy.gui
        self.bundleinfo_patcher = patch(
            'conjure.controllers.deploy.gui.get_bundleinfo')
        self.mock_get_bundleinfo = self.bundleinfo_patcher.start()
        self.mock_bundle = MagicMock()
        self.mock_get_bundleinfo.return_value = ("filename",
                                                 self.mock_bundle,
                                                 [])
        self.finish_patcher = patch(
            'conjure.controllers.deploy.gui.finish')
        self.mock_finish = self.finish_patcher.start()

        self.submit_patcher = patch(
            'conjure.controllers.deploy.gui.async.submit')
        self.mock_submit = self.submit_patcher.start()

    def tearDown(self):
        self.bundleinfo_patcher.stop()
        self.finish_patcher.stop()
        self.submit_patcher.stop()

    def test_queue_predeploy_skipping(self):
        "Test that we do not call predeploy more than once"

        self.gui.is_predeploy_queued = True
        self.gui.render()

        # TEST NOTE: we'd like to have the first ANY here be
        # conjure.controllers.deploy.gui.__do_add_machines so we
        # could check that we call the right thing, but unittest
        # is renaming the module, so that comparison fails.

        # This is one thing that wouldn't be a problem with
        # controllers as classes.
        self.mock_submit.assert_called_once_with(
            ANY, ANY, queue_name=juju.JUJU_ASYNC_QUEUE)

    def test_queue_predeploy_once(self):
        "Call submit to schedule predeploy if we haven't yet"
        self.gui.render()
        print(self.mock_submit.mock_calls)
        assert self.mock_submit.call_count == 2
    
    def test_call_add_machines(self):
        "Call add_machines once"
