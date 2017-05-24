#!/usr/bin/env python
#
# tests controllers/lxdsetup/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, patch

from conjureup import events
from conjureup.controllers.lxdsetup.gui import LXDSetupController


class LXDSetupGUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.utils_patcher = patch(
            'conjureup.controllers.lxdsetup.common.utils')
        self.mock_utils = self.utils_patcher.start()

        self.view_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.LXDSetupView')
        self.mock_view = self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.lxdsetup.common.app')
        mock_app = self.app_patcher.start()
        mock_app.ui = MagicMock(name="app.ui")
        mock_app.env = {'CONJURE_UP_CACHEDIR': '/tmp'}

        self.is_ready = False
        self.ready_patcher = patch.object(LXDSetupController,
                                          'is_ready',
                                          property(lambda s: self.is_ready))
        self.ready_patcher.start()

        self.ifaces = ['eth0', 'wlan0']
        self.ifaces_patcher = patch.object(LXDSetupController,
                                           'ifaces',
                                           property(lambda s: self.ifaces,
                                                    lambda s, v: None),
                                           create=True)
        self.ifaces_patcher.start()

        self.schema_patcher = patch.object(LXDSetupController, 'schema')
        self.schema_patcher.start()

        self.controller = LXDSetupController()
        self.controller.next_screen = MagicMock()
        self.controller.setup = MagicMock()

    def tearDown(self):
        self.utils_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.ready_patcher.stop()
        self.schema_patcher.stop()

    def test_render(self):
        "lxdsetup.gui.test_render"
        self.controller.render()
        assert not self.controller.next_screen.called
        assert not self.controller.setup.called
        assert self.mock_view().show.called

    def test_render_ready(self):
        "lxdsetup.gui.test_render_ready"
        self.is_ready = True
        self.controller.render()
        assert self.controller.next_screen.called
        assert not self.controller.setup.called
        assert not self.mock_view().show.called

    def test_render_no_choice(self):
        "lxdsetup.gui.test_render_no_choice"
        self.ifaces = ['eth0']
        self.controller.render()
        assert not self.controller.next_screen.called
        assert self.controller.setup.called
        assert not self.mock_view().show.called


class LXDSetupGUIFinishTestCase(unittest.TestCase):

    def setUp(self):
        self.controllers_patcher = patch(
            'conjureup.controllers.lxdsetup.common.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.lxdsetup.common.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.lxdsetup.gui.LXDSetupController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.lxdsetup.common.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.mock_app.env = {'CONJURE_UP_CACHEDIR': '/tmp'}
        self.mock_app.current_model = 'conjure-up-bong'
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()
        events.Shutdown.clear()

        self.controller = LXDSetupController()
        self.controller.flag_file = MagicMock()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()

    def test_setup_success(self):
        "lxdsetup.gui.test_setup_success"
        success = MagicMock(returncode=0)
        failure = MagicMock(returncode=1)

        self.mock_utils.run_script.side_effect = [
            success,  # lxc version
            success,  # lxd config
            success,  # lxc storage create default disk
            success,  # lxc profile device add disk
            failure,  # lxc network show conjureup1
            success,  # lxc network create conjureup1
            success,  # lxc network attach-profile
            failure,  # lxc network show conjureup0
            success,  # lxc network create conjureup0
            success,  # lxc network attach-profile
        ]

        self.controller.setup('iface')
        assert self.controller.flag_file.touch.called

    def test_setup_skip(self):
        "lxdsetup.gui.test_bridge_fail"
        success = MagicMock(returncode=0)

        self.mock_utils.run_script.side_effect = [
            success,  # lxc version
            success,  # lxd config
            success,  # lxc storage create default disk
            success,  # lxc profile device add disk
            success,  # lxc network show conjureup1
            success,  # lxc network show conjureup0
        ]

        self.controller.setup('iface')
        assert self.controller.flag_file.touch.called
        assert self.mock_utils.run_script.call_count == 6

    def test_setup_init_fail(self):
        "lxdsetup.gui.test_init_fail"
        failure = MagicMock(returncode=1)

        self.mock_utils.run_script.side_effect = [
            failure,  # lxc version
        ]

        with self.assertRaises(Exception):
            self.controller.setup('iface')
        assert not self.controller.flag_file.touch.called

    def test_setup_bridge_fail(self):
        "lxdsetup.gui.test_bridge_fail"
        success = MagicMock(returncode=0)
        failure = MagicMock(returncode=1)

        self.mock_utils.run_script.side_effect = [
            success,  # lxc version
            success,  # lxd config
            success,  # lxc storage disk
            success,  # lxc profile disk
            failure,  # lxc network show conjureup1
            failure,  # lxc network create conjureup1
        ]

        with self.assertRaises(Exception):
            self.controller.setup('iface')
        assert not self.controller.flag_file.touch.called

    def test_setup_profile_fail(self):
        "lxdsetup.gui.test_profile_fail"
        success = MagicMock(returncode=0)
        failure = MagicMock(returncode=1)

        self.mock_utils.run_script.side_effect = [
            success,  # lxc version
            success,  # lxd init
            success,  # lxc config
            success,  # lxc network create conjureup1
            failure,  # lxc network attach-profile
        ]

        with self.assertRaises(Exception):
            self.controller.setup('iface')
        assert not self.controller.flag_file.touch.called

    def test_setup_unused_bridge_fail(self):
        "lxdsetup.gui.test_unused_bridge_fail"
        success = MagicMock(returncode=0)
        failure = MagicMock(returncode=1)

        self.mock_utils.run_script.side_effect = [
            success,  # lxc version
            success,  # lxd init
            success,  # lxc config
            failure,  # lxc network show conjureup1
            success,  # lxc network create conjureup1
            success,  # lxc network attach-profile
            failure,  # lxc network show conjureup0
            failure,  # lxc network create conjureup0
        ]

        with self.assertRaises(Exception):
            self.controller.setup('iface')
        assert not self.controller.flag_file.touch.called
