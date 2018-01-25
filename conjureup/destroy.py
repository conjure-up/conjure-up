""" Conjure-down entrypoint

Seperate cli application for cleaning up existing controllers
"""

import argparse
import asyncio
import os
import signal
import sys

from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES

from conjureup import __version__ as VERSION
from conjureup import controllers, events, juju, utils
from conjureup.app_config import app
from conjureup.log import setup_logging
from conjureup.ui import ConjureUI


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


async def _start():
    # NB: we have to set the exception handler here because we need to
    # override the one set by urwid, which happens in MainLoop.run()
    app.loop.set_exception_handler(events.handle_exception)

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
    app.log = setup_logging(app,
                            os.path.join(opts.cache_dir, 'conjure-down.log'),
                            opts.debug)

    # Make sure juju paths are setup
    juju.set_bin_path()

    app.env = os.environ.copy()
    app.loop = asyncio.get_event_loop()
    app.loop.add_signal_handler(signal.SIGINT, events.Shutdown.set)
    app.loop.create_task(events.shutdown_watcher())
    app.loop.create_task(_start())

    try:
        if app.argv.controller and app.argv.model:
            app.headless = True
            app.ui = None
            app.env['CONJURE_UP_HEADLESS'] = "1"
            app.loop.run_forever()
        else:
            app.ui = ConjureUI()
            EventLoop.build_loop(app.ui, STYLES,
                                 unhandled_input=events.unhandled_input)
            EventLoop.run()
    finally:
        # explicitly close aysncio event loop to avoid hitting the
        # following issue due to signal handlers added by
        # asyncio.create_subprocess_exec being cleaned up during final
        # garbage collection: https://github.com/python/asyncio/issues/396
        app.loop.close()
