#!/usr/bin/env python
#
# test vsphere configuration
#
# Copyright 2016-2017 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, patch

from conjureup.controllers.vspheresetup.gui import VSphereSetupController


class VSphereSetupGUITestCase(unittest.TestCase):

    def setUp(self):
        self.controllers_patcher = patch(
            'conjureup.controllers.vspheresetup.common.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.vspheresetup.gui.VSphereSetupView')
        self.mock_view = self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.vspheresetup.common.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.controller = VSphereSetupController()
        self.controller.datacenter = MagicMock()

    def tearDown(self):
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.controllers_patcher.stop()

    def test_render(self):
        "vspheresetup.gui.test_render"
        self.controller.render()
        assert self.mock_view().show.called

    def test_finish(self):
        "vspheresetup.gui.test_finish"
        self.controller.finish({
            'primary-network': 'VMNet1',
            'external-network': 'VMNet2',
            'datastore': 'datastore1'
        })
        self.mock_controllers.use.assert_called_once_with('controllerpicker')
