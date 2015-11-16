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
from .parser import Parser, ParserException
from .template import render
from os import makedirs, path
import copy
import tempfile


class Builder:
    def __init__(self, opts):
        """ init

        Pulls in charm metadata and sets up build directory

        Arguments:
        opts: Options passed in from cli
        """
        self.opts = opts
        self.data = {}
        if not opts.build_config:
            raise ParserException("Must pass a --build-config <toml>")
        else:
            self.build_conf = Parser(opts.build_config)

        self.charm = CharmMeta(self.build_conf['charm'])
        self.meta = self.charm.metadata()
        self.build_dir = tempfile.mkdtemp()
        makedirs(path.join(self.build_dir, 'debian'))

    def write_changelog(self):
        """ Write debian/changelog
        """
        ctx = copy.copy(self.meta)
        ctx['maintainer'] = self.charm['maintainer']
        ctx['version'] = self.charm['version']
        ctx['series'] = 'trusty'
        ctx['changelog'] = ['Built by Conjure']
        render(source='debian/changelog',
               target=path.join(self.build_dir, 'debian/changelog'),
               context=ctx)
