""" conjure-craft entrypoint
"""

from conjureup import __version__ as VERSION
from conjureup import utils
from conjureup import charm
from conjureup.app_config import app
from conjureup.log import setup_logging
import argparse
import os
import sys
import yaml


def parse_options(argv):
    parser = argparse.ArgumentParser(prog="conjure-craft")
    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug',
                        help='Enable debug logging.')
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(VERSION))

    subparsers = parser.add_subparsers(help='conjure-craft subcommands help')
    # subparsers.add_parser('init',
    #                       help='Craft a new spell')
    push = subparsers.add_parser('push', help='push spell to registry')
    push.add_argument('path', help='Registry path to push spell to')

    return parser.parse_args(argv)


def main():
    opts = parse_options(sys.argv[1:])

    if os.geteuid() == 0:
        utils.info("")
        utils.info("This should _not_ be run as root or with sudo.")
        utils.info("")
        sys.exit(1)

    if not os.path.isdir('conjure'):
        utils.error('Unable to find required conjure directory for spell.'
                    'Please make sure you are in the correct directory.')
        sys.exit(1)

    if not os.path.isfile('metadata.yaml'):
        utils.error('Unable to find conjure metadata.')
        sys.exit(1)

    # Application Config
    app.argv = opts
    app.log = setup_logging("conjure-up/craft",
                            opts.debug)

    app.env = os.environ.copy()

    utils.info("Pushing spell to registry")
    try:
        spell = charm.push(opts.path)
        utils.info("Applying conjure-up metadata")
        charm.publish(spell)
        charm.grant(spell)
        with open('conjure/metadata.yaml') as fp:
            metadata = yaml.safe_load(fp.read())
        charm.set_metadata(spell, metadata)
        utils.info("Success.")
    except Exception as e:
        utils.error("Unable to push to registry: {}".format(e))
        sys.exit(1)
