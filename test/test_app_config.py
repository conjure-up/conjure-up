#!/usr/bin/env python
#
# tests app_config
#
# Copyright 2016-2017 Canonical, Ltd.


import json
import unittest
from unittest.mock import patch

import fakeredis

from conjureup.app_config import app

from .helpers import AsyncMock, test_loop


class AppConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.expected_keys = [
            'config',
            'bundles',
            'current_bundle',
            'argv',
            'jaas_ok',
            'jaas_controller',
            'is_jaas',
            'current_model',
            'current_controller',
            'current_cloud',
            'current_cloud_type',
            'current_region',
            'current_view',
            'session_id',
            'notrack',
            'noreport',
            'complete',
            'headless',
            'endpoint_type',
            'exit_code'
        ]
        app.state = fakeredis.FakeStrictRedis()
        app.current_controller = "fake-tester-controller"
        app.current_model = "fake-tester-model"
        app.config = {'spell': 'kubernetes-core'}

        self.juju_patcher = patch(
            'conjureup.app_config.app.juju', AsyncMock())
        self.mock_juju = self.juju_patcher.start()
        self.log_patcher = patch(
            'conjureup.app_config.app.log')
        self.mock_log = self.log_patcher.start()

    def tearDown(self):
        self.juju_patcher.stop()
        self.log_patcher.stop()

    def test_config_redis_save(self):
        "app_config.test_config_redis_save"

        self.mock_juju.is_authenticated = False
        with test_loop() as loop:
            loop.run_until_complete(app.save())

        results = app.state.get(app._redis_key)
        json.loads(results.decode('utf8')).keys() == self.expected_keys

    def test_config_juju_model_save(self):
        "app_config.test_config_juju_model_save"

        self.mock_juju.is_authenticated = True
        with test_loop() as loop:
            loop.run_until_complete(app.save())

        assert self.mock_juju.client.set_config.called

    def test_config_juju_model_save_removes_redis_cache(self):
        "app_config.test_config_juju_model_save_remove_redis_cache"

        app.state.set(app._redis_key, "fake data")
        self.mock_juju.is_authenticated = True
        with test_loop() as loop:
            loop.run_until_complete(app.save())

        assert app.state.get(app._redis_key) is None

    def test_config_redis_restore(self):
        "app_config.test_config_redis_restore"
        self.mock_juju.is_authenticated = False

        with test_loop() as loop:
            yield app.save()
            loop.run_until_complete(app.restore())

        results_json = app.state.get(app._redis_key)
        results = json.loads(results_json.decode('utf8'))

        assert app.current_controller == results['current_controller']

    def test_config_juju_restore(self):
        "app_config.test_config_juju_restore"
        class FakeExtraInfo:
            def __init__(self):
                self.value = b'{"current_controller": "moo"}'

        self.mock_juju.is_authenticated = True
        self.mock_juju.client.get_config.return_value = {
            "extra-info": FakeExtraInfo()}
        with test_loop() as loop:
            loop.run_until_complete(app.restore())
        assert app.current_controller == 'moo'
