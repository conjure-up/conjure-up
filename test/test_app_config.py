#!/usr/bin/env python
#
# tests app_config
#
# Copyright 2016-2017 Canonical, Ltd.


import json
import unittest
from unittest.mock import MagicMock

import fakeredis

from conjureup.app_config import AppConfig
from conjureup.models.provider import AWS

from .helpers import AsyncMock, test_loop


class AppConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.expected_keys = [
            'config',
            'provider'
        ]
        self.app = AppConfig()
        self.app.state = fakeredis.FakeStrictRedis()
        self.app.provider = AWS()
        self.app.provider.controller = "fake-tester-controller"
        self.app.provider.model = "fake-tester-model"
        self.app.provider.cloud_type = "ec2"
        self.app.config = {'spell': 'kubernetes-core'}

        self.app.juju.client = AsyncMock()
        self.app.log = MagicMock()

    def test_config_redis_save(self):
        "app_config.test_config_redis_save"
        self.app.juju.authenticated = False
        with test_loop() as loop:
            loop.run_until_complete(self.app.save())

        results = self.app.state.get(self.app._redis_key)
        assert set(json.loads(results.decode('utf8')).keys()) == set(
            self.expected_keys)

    def test_config_juju_model_save(self):
        "app_config.test_config_juju_model_save"

        self.app.juju.authenticated = True
        with test_loop() as loop:
            loop.run_until_complete(self.app.save())

        assert self.app.juju.client.set_config.called

    def test_config_juju_model_save_removes_redis_cache(self):
        "app_config.test_config_juju_model_save_remove_redis_cache"

        self.app.state.set(self.app._redis_key, "fake data")
        self.app.juju.authenticated = True
        with test_loop() as loop:
            loop.run_until_complete(self.app.save())

        assert self.app.state.get(self.app._redis_key) is None

    def test_config_redis_restore(self):
        "app_config.test_config_redis_restore"
        self.app.juju.authenticated = False

        with test_loop() as loop:
            yield self.app.save()
            loop.run_until_complete(self.app.restore())

        results_json = self.app.state.get(self.app._redis_key)
        results = json.loads(results_json.decode('utf8'))

        assert self.app.app.controller == results['controller']

    def test_config_juju_restore(self):
        "app_config.test_config_juju_restore"
        class FakeExtraInfo:
            def __init__(self):
                self.value = b'{"controller": "moo"}'

        self.app.juju.authenticated = True
        self.app.juju.client.get_config.return_value = {
            "extra-info": FakeExtraInfo()}
        with test_loop() as loop:
            loop.run_until_complete(self.app.restore())
        assert self.app.provider.controller == 'moo'

    def test_config_guard_unknown_attribute(self):
        "app_config.test_config_guard_unknown_attribute"
        with self.assertRaises(Exception):
            self.app.chimichanga = "Yum"
