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

from .ev import EventLoop
from .palette import STYLES
from .signals import Signal
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
        self.opts = opts
        self.controllers = {
            "Welcome": None,
            "Config": None,
            "Finalize": None
        }

    def start(self):
        EventLoop.build_loop(WelcomeView(), STYLES)
        EventLoop.run()


def parse_options(argv):
    parser = argparse.ArgumentParser(description="Conjure setup",
                                     prog="conjure-setup")
    parser.add_argument('-c', '--config', dest='build_conf', metavar='CONFIG',
                        help='Path to Conjure config')

    return parser.parse_args(argv)


def main():
    opts = parse_options(sys.argv[1:])

    if not opts.build_conf:
        raise ApplicationException(
            "A conjure config is required, see conjure-setup -h.")

    if not path.exists(opts.build_conf):
        raise ApplicationException("Unable to find {}".format(opts.build_conf))

    app = Application(opts)
    app.start()
