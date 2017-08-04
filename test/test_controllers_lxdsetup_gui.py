#!/usr/bin/env python
#
# tests controllers/lxdsetup/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, patch

from pkg_resources import parse_version

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

        self.ifaces = ['eth0', 'wlan0']
        self.ifaces_patcher = patch.object(LXDSetupController,
                                           'ifaces',
                                           property(lambda s: self.ifaces,
                                                    lambda s, v: None),
                                           create=True)
        self.ifaces_patcher.start()

        self.controller = LXDSetupController()
        self.controller.next_screen = MagicMock()
        self.controller.setup = MagicMock()
        self.controller.set_default_profile = MagicMock()

    def tearDown(self):
        self.utils_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()

    def test_render(self):
        "lxdsetup.gui.test_render"
        self.controller.render()
        assert not self.controller.next_screen.called
        assert not self.controller.setup.called
        assert self.mock_view().show.called

    def test_render_ready(self):
        "lxdsetup.gui.test_render_ready"
        self.controller.render()
        # assert self.controller.next_screen.called
        assert not self.controller.setup.called
        # assert not self.mock_view().show.called

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
        self.parse_version_patcher = patch(
            'conjureup.controllers.lxdsetup.common.parse_version'
        )
        self.mock_parse_version = self.parse_version_patcher.start()
        self.grp_patcher = patch(
            'conjureup.controllers.lxdsetup.common.grp'
        )
        self.mock_grp = self.grp_patcher.start()

        events.Shutdown.clear()

        self.controller = LXDSetupController()
        self.controller.flag_file = MagicMock()
        self.controller.next_screen = MagicMock()
        self.controller.set_default_profile = MagicMock()
        self.controller.can_user_acces_lxd = MagicMock()
        self.controller.kill_dnsmasq = MagicMock()
        self.mock_utils.snap_version.return_value = parse_version('2.25')
        self.mock_utils.get_open_port.return_value = '12001'
        self.mock_parse_version.return_value = parse_version('2.25')

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()
        self.parse_version_patcher.stop()
        self.grp_patcher.stop()

    def test_snap_version_incompatible(self):
        "lxdsetup.gui.test_snap_version_incompatible"
        self.mock_utils.snap_version.return_value = parse_version('2.21')
        with self.assertRaises(Exception):
            self.controller.setup('iface')
        self.mock_utils.snap_version.return_value = parse_version('2.21~14.04')
        with self.assertRaises(Exception):
            self.controller.setup('iface')

    def test_setup_success(self):
        "lxdsetup.gui.test_setup_success"
        success = MagicMock(returncode=0)
        failure = MagicMock(returncode=1)

        self.mock_utils.run_script.side_effect = [
            success,  # lxc version
            failure,  # lxc config get core.https_address
            success,  # lxc config set core.https_address
            success,  # lxc storage create default disk
            failure,  # lxc network show conjureup1
            success,  # lxc network create conjureup1
            success,  # lxc network attach-profile
            failure,  # lxc network show conjureup0
            success,  # lxc network create conjureup0
            success,  # lxc set default profile
        ]

        self.controller.setup('iface')
        assert self.controller.next_screen.called

    def test_setup_skip(self):
        "lxdsetup.gui.test_setup_skip"
        success = MagicMock(returncode=0)

        self.mock_utils.run_script.side_effect = [
            success,  # lxd config get
            success,  # lxc storage create default disk
            success,  # lxc network show conjureup1
            success,  # lxc network show conjureup0
            success,  # lxc set default profile
        ]

        self.controller.setup('iface')
        assert self.mock_utils.run_script.call_count == 5

    def test_setup_init_fail(self):
        "lxdsetup.gui.test_init_fail"
        failure = MagicMock(returncode=1)

        self.mock_utils.run_script.side_effect = [
            failure,  # lxc version
        ]

        with self.assertRaises(Exception):
            self.controller.setup('iface')
        assert not self.controller.next_screen.called

    def test_setup_bridge_fail(self):
        "lxdsetup.gui.test_setup_bridge_fail"
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
        assert not self.controller.next_screen.called

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
        assert not self.controller.next_screen.called

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
            failure,  # lxc network show conjureup0
            failure,  # lxc network create conjureup0
        ]

        with self.assertRaises(Exception):
            self.controller.setup('iface')
        assert not self.controller.next_screen.called
