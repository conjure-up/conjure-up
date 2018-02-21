#!/usr/bin/env python
#
# tests bundle loading, merging, output
#
# Copyright 2016-2018 Canonical, Ltd.


import tempfile
import unittest
from pathlib import Path

import yaml

from conjureup.bundle import Bundle


class BundleTestCase(unittest.TestCase):

    def setUp(self):
        self.tests_dir = Path(__file__).absolute().parent
        self.bundle_dir = self.tests_dir / 'bundle'
        self.bundle_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.bundle_file.close()

    def test_bundle_sanitized(self):
        "bundle.test_bundle_sanitized"
        bundle_yaml = (self.bundle_dir / 'ghost-bundle.yaml').read_text()
        bundle = Bundle(yaml.load(bundle_yaml))
        expected_keys = ['series', 'applications', 'relations']
        assert set(bundle._bundle.keys()) == set(expected_keys)

    def test_bundle_applications(self):
        "bundle.test_bundle_applications"
        bundle_yaml = (self.bundle_dir / 'ghost-bundle.yaml').read_text()
        bundle = Bundle(yaml.load(bundle_yaml))
        expected_apps = ['ghost', 'mysql', 'haproxy']
        assert set(bundle.applications) == set(expected_apps)

    def test_bundle_subtract_fragment(self):
        "bundle.test_bundle_subtract_fragment"
        d = {
            'foo': {
                'bar': 1,
                'baz': 2,
            },
            'qux': [1, 2],
        }
        bundle = Bundle(d)
        bundle.subtract({'foo': None})
        # full key delete
        self.assertEqual(bundle.to_dict(), {'qux': [1, 2]})

        bundle = Bundle(d)
        bundle.subtract({'foo': {'baz': None}})

        # sub-key delete
        self.assertEqual(bundle.to_dict(),
                         {'foo': {'bar': 1}, 'qux': [1, 2]})
