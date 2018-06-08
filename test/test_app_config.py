#!/usr/bin/env python
#
# tests app_config
#
# Copyright 2016-2017 Canonical, Ltd.


import tempfile
import unittest
from unittest.mock import MagicMock

from kv import KV
from ubuntui.widgets.input import StringEditor

from conjureup.app_config import AppConfig
from conjureup.models.provider import AWS, Field, Form

from .helpers import AsyncMock, test_loop


class AppConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.expected_keys = [
            'config',
            'provider'
        ]
        self.app = AppConfig()
        self.db_file = tempfile.NamedTemporaryFile()
        self.app.state = KV(self.db_file.name)
        self.app.provider = AWS()
        self.app.provider.controller = "fake-tester-controller"
        self.app.provider.model = "fake-tester-model"
        self.app.provider.cloud_type = "ec2"
        self.app.config = {'spell': 'kubernetes-core'}

        self.app.juju.client = AsyncMock()
        self.app.log = MagicMock()

    def tearDown(self):
        self.db_file.close()

    def test_provider_form_query_key(self):
        "app_config.provider_form_widget_query_key"
        self.app.provider.form = Form(
            [Field(label='test widget',
                   widget=StringEditor(default='hai2u'),
                   key='test-key')])
        assert self.app.provider.form.field('test-key').value == 'hai2u'

    @unittest.skip("FIXME: Finish save/restore "
                   "state for juju model config")
    def test_config_juju_model_save(self):
        "app_config.test_config_juju_model_save"

        self.app.juju.authenticated = True
        with test_loop() as loop:
            loop.run_until_complete(self.app.save())

        assert self.app.juju.client.set_config.called

    @unittest.skip("FIXME: Finish save/restore "
                   "state for juju model config")
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
