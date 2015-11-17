# Copyright (c) 2015 Canonical Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

""" Builder entrypoint

This class handles the build tasks for generating a deb package
"""

from .charm import CharmMeta
from .parser import Parser
from .template import render
from os import path
import copy
import argparse
import sys
import shutil
import logging
import textwrap

log = logging.getLogger('builder')


class BuilderException(Exception):
    """ Problem in builder
    """
    pass


class Builder:
    def __init__(self, opts):
        """ init

        Pulls in charm metadata and sets up build directory

        Arguments:
        build_conf: Build configuration
        dist_dir: Output directory for finished build
        """
        self.opts = opts
        self.build_conf = Parser(opts.build_conf)
        self.dist_dir = opts.dist_dir
        self.charm = CharmMeta(self.build_conf['name'])

    def context(self):
        """ Generate dictionary for writing to debian directory
        """
        meta = self.charm.metadata
        ctx = copy.copy(meta)
        ctx.update(**self.charm.id)
        ctx['Maintainer'] = self.build_conf['maintainer']
        ctx['Version'] = self.build_conf['version']
        ctx['Description'] = "\n".join([' {}'.format(l) for l in
                                        textwrap.wrap(ctx['Description'], 79)])
        ctx['Changelog'] = ['Built by Conjure']
        return ctx

    def render(self):
        """ Writes out debian template files to dist directory
        """
        deb_dir = path.join(self.dist_dir, 'debian')
        for fname in ['changelog', 'control', 'postinst']:
            render(source="debian/{}".format(fname),
                   target=path.join(deb_dir, fname),
                   context=self.context())
        # Render .install file
        paths = {'InstallPaths': [
            ('conjurebuild.toml',
             'usr/share/conjure/{}'.format(self.context()['Name']))
        ]}
        render(source="debian/install",
               target=path.join(deb_dir,
                                "{}.install".format(self.context()['Name'])),
               context=paths)


def parse_options(argv):
    parser = argparse.ArgumentParser(description="Conjure builder",
                                     prog="conjure-build")
    parser.add_argument('-i', '--initialize', action='store_true',
                        dest='initialize',
                        help='Initialize a conjure project')
    parser.add_argument('-c', '--config', dest='build_conf', metavar='CONFIG',
                        help='Path to Conjure build config')
    parser.add_argument('-o', '--output', dest='dist_dir',
                        help='Output directory', metavar='DIR')

    return parser.parse_args(argv)


def main():
    opts = parse_options(sys.argv[1:])

    if opts.initialize:
        if path.exists(path.join(opts.dist_dir)):
            raise BuilderException(
                "Initalize was started but destination "
                "directory already exists.")
        shutil.copytree('templates', opts.dist_dir)
        print("Initialized: {}".format(opts.dist_dir))
        sys.exit(0)

    if not opts.build_conf:
        raise BuilderException(
            "A build config is required, see conjure-build help.")
    builder = Builder(opts)
    builder.render()
