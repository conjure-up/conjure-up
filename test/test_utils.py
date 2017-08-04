#!/usr/bin/env python
#
# tests test/utils.py
#
# Copyright Canonical, Ltd.


import asyncio
import logging
import unittest
from unittest.mock import patch

from conjureup import utils

from .helpers import test_loop


class UtilsTestCase(unittest.TestCase):

    def test_valid_hostnames(self):
        "Verify is_valid_hostname"

        hostnames = [
            'battlemidget.lol',
            'www.battlemidget.lol',
            'localhost',
            'localhost.localdomain',
            '_underscores-is_ok',
            'double--dash_is_ok'
        ]
        for hostname in hostnames:
            assert utils.is_valid_hostname(hostname)

    def test_invalid_hostnames(self):
        "Verify is_valid_hostname detects invalid hostnames"

        hostnames = [
            '-no-starting-dash.com',
            '.localhost',
            'localhost.no-end-dash-'
        ]
        for hostname in hostnames:
            assert not utils.is_valid_hostname(hostname)

    @patch.object(utils, 'juju_version')
    @patch.object(utils, 'lxd_version')
    @patch.object(utils, 'app')
    def test_sentry_report(self, app, lxd_version, juju_version):
        # test task schedule
        flag = asyncio.Event()
        with patch.object(utils, '_sentry_report',
                          lambda *a, **kw: flag.set()):
            with test_loop() as loop:
                app.loop = loop
                utils.sentry_report('m')
                loop.run_until_complete(asyncio.wait_for(flag.wait(), 30))

        # test implementation
        app.config = {'spell': 'spell'}
        app.provider.cloud_type = 'type'
        app.provider.region = 'region'
        app.is_jaas = False
        app.headless = False
        juju_version.return_value = '2.j'
        lxd_version.return_value = '2.l'

        app.noreport = True
        utils._sentry_report('message', tags={'foo': 'bar'})
        assert not app.sentry.capture.called

        app.noreport = False
        utils._sentry_report('message', tags={'foo': 'bar'})
        app.sentry.capture.assert_called_once_with(
            'raven.events.Message',
            message='message',
            level=logging.WARNING,
            tags={
                'spell': 'spell',
                'cloud_type': 'type',
                'region': 'region',
                'jaas': False,
                'headless': False,
                'juju_version': '2.j',
                'lxd_version': '2.l',
                'foo': 'bar',
            })

        app.sentry.capture.reset_mock()
        utils._sentry_report('message', 'exc_info')
        app.sentry.capture.assert_called_once_with(
            'raven.events.Exception',
            level=logging.ERROR,
            exc_info='exc_info',
            tags={
                'spell': 'spell',
                'cloud_type': 'type',
                'region': 'region',
                'jaas': False,
                'headless': False,
                'juju_version': '2.j',
                'lxd_version': '2.l',
            })
