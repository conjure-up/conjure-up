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

""" Application entrypoint
"""

from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES
from conjure.juju import Juju
from conjure.controllers.welcome import WelcomeController
from conjure.ui import ConjureUI
from conjure.models.jujumodels.local import LocalJujuModel
from conjure.models.jujumodels.maas import MaasJujuModel
from conjure.models.jujumodels.openstack import OpenStackJujuModel
from conjure import async
import json
import sys
import argparse
import os.path as path


class ApplicationException(Exception):
    """ Error in application
    """
    pass


class Application:
    def __init__(self, opts):
        """ init

        Arguments:
        opts: Options passed in from cli
        """
        with open(opts.build_conf) as json_f:
            config = json.load(json_f)

        with open(opts.build_metadata) as json_f:
            config['metadata'] = json.load(json_f)

        with open('/usr/share/conjure/providers.json') as json_f:
            config['juju-models'] = json.load(json_f)

        self.common = {
            'opts': opts,
            'ui': ConjureUI(),
            'config': config,
            'juju': Juju
        }

    def unhandled_input(self, key):
        if key in ['q', 'Q']:
            async.shutdown()
            EventLoop.exit(0)

    def _start(self, *args, **kwargs):
        """ Initially load the welcome screen
        """
        WelcomeController(self.common).render()

    def start(self):
        EventLoop.build_loop(self.common['ui'], STYLES,
                             unhandled_input=self.unhandled_input)
        EventLoop.set_alarm_in(0.05, self._start)
        EventLoop.run()


def parse_options(argv):
    parser = argparse.ArgumentParser(description="Conjure setup",
                                     prog="conjure-setup")
    parser.add_argument('-c', '--config', dest='build_conf', metavar='CONFIG',
                        help='Path to Conjure config')
    parser.add_argument('-m', '--metadata', dest='build_metadata',
                        metavar='METADATA',
                        help='Path to bundle services metadata')

    return parser.parse_args(argv)


def main():
    opts = parse_options(sys.argv[1:])

    if not opts.build_conf:
        raise ApplicationException(
            "A conjure config is required, see conjure-setup -h.")

    if not path.exists(opts.build_conf):
        raise ApplicationException("Unable to find {}".format(opts.build_conf))

    if not path.exists(opts.build_metadata):
        raise ApplicationException("Unable to find {} metadata".format(
            opts.build_metadata
        ))

    app = Application(opts)
    app.start()
