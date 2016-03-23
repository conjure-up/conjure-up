""" Application entrypoint
"""

from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES
from conjure.ui import ConjureUI
from conjure import async
from conjure import __version__ as VERSION
from conjure.controllers.welcome import WelcomeController
from conjure.controllers.finish import FinishController
from conjure.controllers.deploysummary import DeploySummaryController
from conjure.controllers.deploy import DeployController
from conjure.controllers.cloud import CloudController
from conjure.controllers.newcloud import NewCloudController
from conjure.controllers.jujucontroller import JujuControllerController
from conjure.controllers.bootstrapwait import BootstrapWaitController
from conjure.log import setup_logging
import json
import sys
import argparse
import os.path as path
import logging


log = logging.getLogger('app')


class ApplicationException(Exception):
    """ Error in application
    """


class ApplicationConfig:
    """ Application config encapsulating common attributes
    used throughout the lifetime of the application.
    """
    def __init__(self):
        self.ui = None
        self.config = None
        self.argv = None
        self.controllers = None
        self.current_model = None
        self.log = None


class Application:
    def __init__(self, argv):
        """ init

        Arguments:
        argv: Options passed in from cli
        """
        self.app = ApplicationConfig()
        self.app.argv = argv
        self.app.ui = ConjureUI()

        with open(argv.build_conf) as json_f:
            config = json.load(json_f)

        with open(argv.build_metadata) as json_f:
            config['metadata_filename'] = path.abspath(argv.build_metadata)
            config['metadata'] = json.load(json_f)

        self.app.config = config
        self.app.log = setup_logging(self.app.config['name'],
                                     debug=self.app.argv.debug)

        self.app.controllers = {
            'welcome': WelcomeController(self.app),
            'clouds': CloudController(self.app),
            'newcloud': NewCloudController(self.app),
            'bootstrapwait': BootstrapWaitController(self.app),
            'deploy': DeployController(self.app),
            'deploysummary': DeploySummaryController(self.app),
            'jujucontroller': JujuControllerController(self.app),
            'finish': FinishController(self.app)
        }

    def unhandled_input(self, key):
        if key in ['q', 'Q']:
            async.shutdown()
            EventLoop.exit(0)

    def _start(self, *args, **kwargs):
        """ Initially load the welcome screen
        """
        if self.app.argv.status_only:
            self.app.controllers['finish'].render()
        else:
            self.app.controllers['welcome'].render()

    def start(self):
        EventLoop.build_loop(self.app.ui, STYLES,
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
    parser.add_argument('-s', '--status', action='store_true',
                        dest='status_only',
                        help='Only display the Status of '
                        'existing deployed bundled.')
    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug',
                        help='Enable debug logging.')
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(VERSION))
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
