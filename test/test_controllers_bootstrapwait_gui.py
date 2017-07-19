#!/usr/bin/env python
#
# tests controllers/bootstrapwait/gui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, call, patch, sentinel

from conjureup import events
from conjureup.controllers.bootstrapwait.gui import BootstrapWaitController

from .helpers import test_loop


class BootstrapwaitGUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = BootstrapWaitController()

        self.controller.refresh = MagicMock(return_value=sentinel.refresh)
        self.controller.finish = MagicMock(return_value=sentinel.finish)

        self.finish_patcher = patch(
            'conjureup.controllers.bootstrapwait.gui.'
            'BootstrapWaitController.finish')
        self.mock_finish = self.finish_patcher.start()

        self.controllers_patcher = patch(
            'conjureup.controllers.bootstrapwait.gui.'
            'controllers')
        self.mock_controllers = self.controllers_patcher.start()
        self.view_patcher = patch(
            'conjureup.controllers.bootstrapwait.gui.BootstrapWaitView')
        self.view_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.bootstrapwait.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()

        self.track_screen_patcher = patch(
            'conjureup.controllers.bootstrapwait.gui.track_screen')
        self.mock_track_screen = self.track_screen_patcher.start()
        events.Bootstrapped.clear()

    def tearDown(self):
        self.finish_patcher.stop()
        self.view_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()
        self.track_screen_patcher.stop()

    def test_render(self):
        "call render"
        events.Bootstrapped.set()
        self.controller.render()
        assert not self.mock_app.loop.create_task.called

        events.Bootstrapped.clear()
        self.controller.render()
        self.assertEqual(self.mock_app.loop.create_task.mock_calls, [
            call(sentinel.refresh),
            call(sentinel.finish)])


class BootstrapwaitGUIFinishTestCase(unittest.TestCase):

    def setUp(self):
        self.controller = BootstrapWaitController()

        self.controllers_patcher = patch(
            'conjureup.controllers.bootstrapwait.gui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.bootstrapwait.gui.'
            'BootstrapWaitController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.bootstrapwait.gui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()

        self.asleep_patcher = patch('asyncio.sleep')
        self.mock_asleep = self.asleep_patcher.start()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()
        self.asleep_patcher.stop()

    def test_refresh(self):
        "call refresh"
        async def set_bs():
            events.Bootstrapped.set()

        events.Bootstrapped.clear()
        self.mock_asleep.return_value = set_bs()
        mock_view = MagicMock()
        with test_loop() as loop:
            loop.run_until_complete(self.controller.refresh(mock_view))
        mock_view.redraw_kitt.assert_called_once_with()

    def test_finish(self):
        "call finish"
        events.Bootstrapped.set()
        with test_loop() as loop:
            loop.run_until_complete(self.controller.finish())
        self.mock_controllers.use.assert_called_once_with('deploy')
