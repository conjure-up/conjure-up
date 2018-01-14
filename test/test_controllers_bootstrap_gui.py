#!/usr/bin/env python
#
# tests controllers/bootstrap/gui.py
#
# Copyright 2016 Canonical, Ltd.


import asyncio
import unittest
from unittest.mock import MagicMock, call, patch, sentinel

from conjureup import events
from conjureup.controllers.bootstrap.gui import BootstrapController

from .helpers import AsyncMock, test_loop


class BootstrapGUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = BootstrapController()

        self.controller.do_add_model = AsyncMock()
        self.controller.do_bootstrap = AsyncMock()
        self.controller.wait = MagicMock(
            return_value=sentinel.wait)
        self.controller.is_existing_controller = MagicMock()

        self.controllers_patcher = patch(
            'conjureup.controllers.bootstrap.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()
        self.view_patcher = patch(
            'conjureup.controllers.bootstrap.gui.InterstitialView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.bootstrap.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.mock_app.config = {'spell-dir': '/tmp'}
        self.mock_app.provider = AsyncMock()
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()
        self.common_app_patcher = patch(
            'conjureup.controllers.bootstrap.common.app', self.mock_app)
        self.common_app_patcher.start()

        events.Bootstrapped.clear()

    def tearDown(self):
        events.Bootstrapped.clear()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()
        self.common_app_patcher.stop()

    def test_render(self):
        self.controller.run = MagicMock(return_value=sentinel.run)
        self.controller.render()
        self.assertEqual(self.mock_app.loop.create_task.mock_calls, [
            call(sentinel.run),
            call(sentinel.wait)])

    def test_run_jaas(self):
        "call render"
        self.mock_app.is_jaas = True
        self.controller.is_existing_controller.return_value = False
        with test_loop() as loop:
            loop.run_until_complete(self.controller.run())
        assert self.mock_app.provider.configure_tools.called
        assert self.controller.do_add_model.called

    def test_run_existing(self):
        "call render"
        self.mock_app.is_jaas = False
        self.controller.is_existing_controller.return_value = True
        with test_loop() as loop:
            loop.run_until_complete(self.controller.run())
        assert self.mock_app.provider.configure_tools.called
        assert self.controller.do_add_model.called

    def test_run_bootstrap(self):
        "call render"
        self.mock_app.is_jaas = False
        self.controller.is_existing_controller.return_value = False
        with test_loop() as loop:
            loop.run_until_complete(self.controller.run())
        assert self.mock_app.provider.configure_tools.called
        assert self.controller.do_bootstrap.called


class BootstrapGUIWaitTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = BootstrapController()

        self.controllers_patcher = patch(
            'conjureup.controllers.bootstrap.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.bootstrap.gui.BootstrapController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.bootstrap.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()

    def tearDown(self):
        events.Bootstrapped.clear()
        self.controllers_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()

    def test_wait(self):
        async def set_bs():
            await asyncio.sleep(0.1)
            events.Bootstrapped.set()

        events.Bootstrapped.clear()
        with test_loop() as loop:
            loop.run_until_complete(asyncio.gather(
                self.controller.wait(),
                set_bs(),
            ))
        self.mock_controllers.use.assert_called_once_with('deploy')
