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

from . import toml
from .charm import query_cs
from .parser import Parser
from .template import render
from .utils import FS
from os import path
import time
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
        self.charm = query_cs(self.build_conf['name'])
        self._update_build_conf()

    def _wrap_description(self, description):
        """ Indents description
        """
        return "\n".join([' {}'.format(l) for l in
                         textwrap.wrap(description, 79)])

    def timestamp(self):
        """ Formats current datetime
        """
        return time.strftime('%a, %d %b %Y %X %z')

    def _update_build_conf(self):
        """ Updates conjure build config
        """
        charm_config = self.charm['Meta']['charm-config']['Options']
        charm_meta = self.charm['Meta']['charm-metadata']
        self.build_conf['fields'] = charm_config
        self.build_conf['name'] = charm_meta['Name']
        self.build_conf['summary'] = charm_meta['Summary']
        self.build_conf['description'] = self._wrap_description(
            charm_meta['Description'])
        self.build_conf['changelog'] = ['Automatic conjure build']
        self.build_conf['series'] = self.opts.series
        self.build_conf['timestamp'] = self.timestamp()
        FS.spew(self.opts.build_conf, toml.dumps(self.build_conf.to_dict))

    def render(self):
        """ Writes out debian template files to dist directory
        """
        deb_dir = path.join(self.dist_dir, 'debian')
        for fname in ['changelog', 'control', 'postinst']:
            render(source="debian/{}".format(fname),
                   target=path.join(deb_dir, fname),
                   context=self.build_conf.to_dict)
        # Render .install file
        paths = {'InstallPaths': [
            ('conjurebuild.toml',
             'usr/share/conjure/{}'.format(self.build_conf['name']))
        ]}
        render(source="debian/install",
               target=path.join(deb_dir,
                                "{}.install".format(self.build_conf['name'])),
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
    parser.add_argument('-s', '--series', dest='series',
                        default='trusty', help='Ubuntu Series to build for.')

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
