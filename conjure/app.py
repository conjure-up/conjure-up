""" Application entrypoint
"""

from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES
from conjure.ui import ConjureUI
from conjure.juju import Juju
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
import os
import os.path as path
import uuid


class ApplicationException(Exception):
    """ Error in application
    """


class ApplicationConfig:
    """ Application config encapsulating common attributes
    used throughout the lifetime of the application.
    """
    def __init__(self):
        # Reference to entire UI
        self.ui = None
        # Global config attr
        self.config = None
        # CLI arguments
        self.argv = None
        # List of all known controllers to be rendered
        self.controllers = None
        # Current Juju model
        self.current_model = None
        # Global session id
        self.session_id = os.getenv('CONJURE_TEST_SESSION_ID',
                                    str(uuid.uuid4()))
        # Logger
        self.log = None
        # Environment to pass to processing tasks
        self.env = os.environ.copy()


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

        self.app.log = setup_logging(self.app.config['name'],
                                     self.app.argv.debug)

    def unhandled_input(self, key):
        if key in ['q', 'Q']:
            async.shutdown()
            EventLoop.exit(0)

    def _start(self, *args, **kwargs):
        """ Initially load the welcome screen
        """
        if self.app.argv.status_only:
            self.app.controllers['finish'].render(bundle=None)
        else:
            self.app.controllers['welcome'].render()

    def start(self):
        EventLoop.build_loop(self.app.ui, STYLES,
                             unhandled_input=self.unhandled_input)
        EventLoop.set_alarm_in(0.05, self._start)
        EventLoop.run()


def parse_options(argv):
    parser = argparse.ArgumentParser(prog="conjure-setup")
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
    if os.geteuid() == 0:
        print("")
        print("This should _not_ be run as root or with sudo.")
        print("")
        sys.exit(1)

    opts = parse_options(sys.argv[1:])

    try:
        docs_url = "https://jujucharms.com/docs/stable/getting-started"
        juju_version = Juju.version()
        if int(juju_version[0]) < 2:
            print(
                "Only Juju v2 and above is supported, "
                "your currently installed version is {}.\n\n"
                "Please refer to {} for help on installing "
                "the correct Juju.".format(juju_version, docs_url))
            sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)

    if not opts.build_conf:
        print(
            "A conjure config is required, see conjure-setup -h.")
        sys.exit(1)

    if not path.exists(opts.build_conf):
        print("Unable to find {}".format(opts.build_conf))
        sys.exit(1)

    if not path.exists(opts.build_metadata):
        print("Unable to find {} metadata".format(
            opts.build_metadata
        ))
        sys.exit(1)

    app = Application(opts)
    app.start()
