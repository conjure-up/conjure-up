#!/usr/bin/env python
#
# tests test/utils.py
#
# Copyright Canonical, Ltd.


import unittest

from conjureup import utils


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
