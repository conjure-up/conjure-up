#!/usr/bin/env python
#
# tests controllers/deploy/common.py
#
# Copyright 2016 Canonical, Ltd.


import asyncio
import unittest
from unittest.mock import MagicMock, patch

from conjureup.controllers.deploy import common

from .helpers import AsyncMock, test_loop


class DeployCommonDoDeployTestCase(unittest.TestCase):

    def setUp(self):
        async def dummy():
            pass

        self.app_patcher = patch(
            'conjureup.controllers.deploy.common.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.events_app_patcher = patch('conjureup.events.app', self.mock_app)
        self.events_app_patcher.start()
        self.utils_patcher = patch(
            'conjureup.controllers.deploy.common.utils'
        )
        self.mock_utils = self.utils_patcher.start()
        self.juju_patcher = patch(
            'conjureup.controllers.deploy.common.juju')
        self.mock_juju = self.juju_patcher.start()
        self.mock_app.juju.client.deploy = AsyncMock()

    def tearDown(self):
        self.app_patcher.stop()
        self.utils_patcher.stop()
        self.events_app_patcher.stop()
        self.juju_patcher.stop()

    @patch('conjureup.controllers.deploy.common.os.path.join')
    def test_do_deploy(self, mock_join):
        "call do_deploy"
        mock_join.return_value = '/tmp/path'
        msg_cb = MagicMock()
        with test_loop() as loop:
            # have to patch out the event because the existing one is
            # attached to a different event loop
            new_event = asyncio.Event(loop=loop)
            new_event.set()
            with patch('conjureup.events.ModelConnected', new_event):
                loop.run_until_complete(common.do_deploy(msg_cb))

        assert self.mock_app.juju.client.deploy.called
