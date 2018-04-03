#!/usr/bin/env python
#
# tests bundle loading, merging, output
#
# Copyright 2016-2018 Canonical, Ltd.


import argparse
import unittest
from pathlib import Path

from conjureup.models.conjurefile import Conjurefile


class ConjurefileTestCase(unittest.TestCase):

    def setUp(self):
        self.tests_dir = Path(__file__).absolute().parent
        self.conjurefile_path = self.tests_dir / 'Conjurefile'
        self.conjurefile = Conjurefile.load([self.conjurefile_path])

    def test_conjurefile_argv_override(self):
        "conjurefile.test_argv_override"
        args = argparse.Namespace()
        args.registry = 'https://github.com/conjure-up/spells.git'
        assert self.conjurefile['registry'] == (
            'https://github.com/battlemidget/spells.git')
        self.conjurefile.merge_argv(args)
        assert self.conjurefile['registry'] == (
            'https://github.com/conjure-up/spells.git')

    def test_conjurefile_debug_enabled(self):
        "conjurefile.test_debug_enabled"
        assert self.conjurefile['debug']

    def test_conjurefile_melddict_level_1(self):
        "conjurefile.test_melddict_level_1"
        assert self.conjurefile['cloud'] == 'aws'

    def test_conjurefile_melddict_level_2(self):
        "conjurefile.test_melddict_level_2"
        self.conjurefile_path2 = self.tests_dir / 'Conjurefile2'
        self.conjurefile = Conjurefile.load([
            self.conjurefile_path,
            self.conjurefile_path2
        ])
        assert self.conjurefile['cloud'] == 'gce'

    def test_conjurefile_argv_spell_cloud(self):
        "conjurefile.test_argv_spell_cloud"
        args = argparse.Namespace()
        args.spell = 'canonical-kubernetes'
        args.cloud = 'aws/us-east-1'
        self.conjurefile.merge_argv(args)
        assert self.conjurefile['spell'] == 'canonical-kubernetes'
        assert self.conjurefile['cloud'] == 'aws/us-east-1'
