""" Conjure-down entrypoint

Seperate cli application for cleaning up existing controllers
"""

import argparse
import os
import sys

from conjureup import __version__ as VERSION
from conjureup import async, controllers, utils
from conjureup.app_config import app
from conjureup.log import setup_logging
from conjureup.ui import ConjureUI
from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES


def parse_options(argv):
    parser = argparse.ArgumentParser(prog="conjure-down")
    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug',
                        help='Enable debug logging.')
    parser.add_argument('--cache-dir', dest='cache_dir',
                        help='Download directory for spells',
                        default=os.path.expanduser("~/.cache/conjure-up"))
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('--notrack', action='store_true',
                        dest='notrack',
                        help='Opt out of sending anonymous usage '
                        'information to Canonical.')
    parser.add_argument('controller', nargs='?',
                        help="Name of a juju controller to target.")
    parser.add_argument('model', nargs='?',
                        help="Name of a juju model to target. "
                        "A controller is required.")

    return parser.parse_args(argv)


def unhandled_input(key):
    if key in ['q', 'Q']:
        async.shutdown()
        EventLoop.exit(0)


def _start(*args, **kwargs):
    controllers.use('destroy').render()


def main():
    opts = parse_options(sys.argv[1:])

    if os.geteuid() == 0:
        utils.info("")
        utils.info("This should _not_ be run as root or with sudo.")
        utils.info("")
        sys.exit(1)

    if not os.path.isdir(opts.cache_dir):
        os.makedirs(opts.cache_dir)

    # Application Config
    app.config = {'metadata': None}
    app.argv = opts
    app.log = setup_logging("conjure-down",
                            os.path.join(opts.cache_dir, 'conjure-down.log'),
                            opts.debug)

    app.env = os.environ.copy()

    if app.argv.controller and app.argv.model:
        app.headless = True
        app.ui = None
        app.env['CONJURE_UP_HEADLESS'] = "1"
        _start()

    app.ui = ConjureUI()
    EventLoop.build_loop(app.ui, STYLES,
                         unhandled_input=unhandled_input)
    EventLoop.set_alarm_in(0.05, _start)
    EventLoop.run()
