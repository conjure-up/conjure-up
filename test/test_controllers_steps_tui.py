#!/usr/bin/env python
#
# tests controllers/steps/tui.py
#
# Copyright 2016 Canonical, Ltd.


import unittest
from unittest.mock import MagicMock, patch

from conjureup import events
from conjureup.controllers.steps.tui import StepsController

from .helpers import test_loop


class StepsTUIRenderTestCase(unittest.TestCase):

    def setUp(self):
        self.do_steps_patcher = patch(
            'conjureup.controllers.steps.tui.StepsController.do_steps')
        self.mock_do_steps = self.do_steps_patcher.start()

        self.app_patcher = patch(
            'conjureup.controllers.steps.tui.app')
        self.mock_app = self.app_patcher.start()
        self.controller = StepsController()

    def tearDown(self):
        self.do_steps_patcher.stop()
        self.app_patcher.stop()

    def test_render(self):
        "call render"
        self.controller.render()
        self.mock_app.loop.create_task.called_once_with(self.mock_do_steps())


class StepsTUIFinishTestCase(unittest.TestCase):

    def setUp(self):
        self.controllers_patcher = patch(
            'conjureup.controllers.steps.tui.controllers')
        self.mock_controllers = self.controllers_patcher.start()

        self.utils_patcher = patch(
            'conjureup.controllers.steps.tui.utils')
        self.mock_utils = self.utils_patcher.start()

        self.render_patcher = patch(
            'conjureup.controllers.steps.tui.StepsController.render')
        self.mock_render = self.render_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.steps.tui.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.ev_app_patcher = patch(
            'conjureup.events.app', self.mock_app)
        self.ev_app_patcher.start()
        self.common_patcher = patch(
            'conjureup.controllers.steps.tui.common')
        self.mock_common = self.common_patcher.start()
        self.controller = StepsController()
        events.Shutdown.clear()

    def tearDown(self):
        self.controllers_patcher.stop()
        self.utils_patcher.stop()
        self.render_patcher.stop()
        self.app_patcher.stop()
        self.ev_app_patcher.stop()
        self.common_patcher.stop()

    def test_do_steps(self):
        "call do_steps"
        responses = ['result1', 'result2']
        results = {'title2': 'result1',
                   'title3': 'result2'}

        async def dummy():
            return responses.pop(0)

        self.mock_common.get_step_metadata_filenames.side_effect = [['sudo_n',
                                                                     'sudo_y'],
                                                                    ['sudo_y',
                                                                     'nosudo']]
        self.mock_common.load_step.side_effect = [MagicMock(needs_sudo=True,
                                                            title='title1'),
                                                  MagicMock(needs_sudo=True,
                                                            title='title2'),
                                                  MagicMock(needs_sudo=False,
                                                            title='title3')]
        self.mock_utils.is_linux.return_value = True
        self.mock_utils.can_sudo.side_effect = [False, True, False]
        self.mock_common.do_step.side_effect = [dummy(), dummy()]

        with test_loop() as loop:
            loop.run_until_complete(self.controller.do_steps())
            assert events.Shutdown.is_set()
            assert not self.mock_controllers.use.called

            events.Shutdown.clear()
            loop.run_until_complete(self.controller.do_steps())
            assert not events.Shutdown.is_set()
            self.mock_controllers.use.assert_called_once_with('summary')
            self.mock_controllers.use().render.assert_called_once_with(results)
