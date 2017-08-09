#!/usr/bin/env python
#
# tests controllers/deploy/common.py
#
# Copyright 2016 Canonical, Ltd.


import asyncio
import unittest
from unittest.mock import MagicMock, patch

from conjureup.controllers.deploy import common

from .helpers import test_loop


class DeployCommonDoDeployTestCase(unittest.TestCase):

    def setUp(self):
        async def dummy():
            pass

        self.pre_deploy_patcher = patch(
            'conjureup.controllers.deploy.common.pre_deploy')
        self.mock_pre_deploy = self.pre_deploy_patcher.start()
        self.app_patcher = patch(
            'conjureup.controllers.deploy.common.app')
        self.mock_app = self.app_patcher.start()
        self.mock_app.ui = MagicMock(name="app.ui")
        self.events_app_patcher = patch('conjureup.events.app', self.mock_app)
        self.events_app_patcher.start()
        self.juju_patcher = patch(
            'conjureup.controllers.deploy.common.juju')
        self.mock_juju = self.juju_patcher.start()

        self.mock_pre_deploy.return_value = dummy()
        self.mock_juju.add_machines.return_value = dummy()
        self.mock_juju.deploy_service.return_value = dummy()
        self.mock_juju.set_relations.return_value = dummy()

    def tearDown(self):
        self.pre_deploy_patcher.stop()
        self.app_patcher.stop()
        self.events_app_patcher.stop()
        self.juju_patcher.stop()

    def test_do_deploy(self):
        "call do_deploy"
        self.mock_app.metadata_controller.bundle.services = [
            MagicMock(service_name='service'),
        ]

        msg_cb = MagicMock()
        with test_loop() as loop:
            # have to patch out the event because the existing one is
            # attached to a different event loop
            new_event = asyncio.Event(loop=loop)
            new_event.set()
            with patch('conjureup.events.ModelConnected', new_event):
                loop.run_until_complete(common.do_deploy(msg_cb))

        assert self.mock_pre_deploy.called
        assert self.mock_juju.add_machines.called
        assert self.mock_juju.deploy_service.called
        assert self.mock_juju.set_relations.called
