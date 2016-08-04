""" Application entrypoint
"""

from conjureup import __version__ as VERSION
from conjureup import async
from conjureup import consts
from conjureup import controllers
from conjureup import juju
from conjureup import utils
from conjureup import charm
from conjureup.app_config import app
from conjureup.download import (download, download_local,
                                get_remote_url, fetcher)
from conjureup.log import setup_logging
from conjureup.ui import ConjureUI


from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES

import argparse
import os
import os.path as path
import sys
import uuid
import yaml


def parse_options(argv):
    parser = argparse.ArgumentParser(prog="conjure-up")
    parser.add_argument('spell', nargs='?',
                        default=consts.UNSPECIFIED_SPELL,
                        help="""The name ('openstack-nclxd') or location
                        ('githubusername/spellrepo') of a conjure-up
                        spell, or a keyword matching multiple spells
                        e.g. openstack""")
    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug',
                        help='Enable debug logging.')
    parser.add_argument('-s', '--status', action='store_true',
                        dest='status_only',
                        help='Display the summary of the conjuring')
    parser.add_argument('-c', dest='global_config_file',
                        help='Location of conjure-up.conf',
                        default='/etc/conjure-up.conf')
    parser.add_argument('--cache_dir', dest='cache_dir',
                        help='Download directory for spells',
                        default=os.path.expanduser("~/.cache/conjure-up"))
    parser.add_argument('--spells-dir', dest='spells_dir',
                        help='Location of readonly packaged spells directory',
                        default='/usr/share/conjure-up/spells')
    parser.add_argument('--apt-proxy', dest='apt_http_proxy',
                        help='Specify APT proxy')
    parser.add_argument('--apt-https-proxy', dest='apt_https_proxy',
                        help='Specify APT HTTPS proxy')
    parser.add_argument('--http-proxy', dest='http_proxy',
                        help='Specify HTTP proxy')
    parser.add_argument('--https-proxy', dest='https_proxy',
                        help='Specify HTTPS proxy')
    parser.add_argument('--proxy-proxy', dest='no_proxy',
                        help='Comma separated list of IPs to not '
                        'filter through a proxy')
    parser.add_argument('--bootstrap-timeout', dest='bootstrap_timeout',
                        help='Amount of time to wait for initial controller '
                        'creation. Useful for slower network connections.')
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(VERSION))

    subparsers = parser.add_subparsers(help='sub-command help')
    parse_to = subparsers.add_parser('to',
                                     help='Indicate which cloud to deploy to')
    parse_to.add_argument('cloud', help='Name of a public cloud')
    return parser.parse_args(argv)


def unhandled_input(key):
    if key in ['q', 'Q']:
        async.shutdown()
        EventLoop.exit(0)


def _start(*args, **kwargs):
    if app.fetcher is None:
        controllers.use('recommended').render()
        return

    if app.fetcher != 'charmstore-search':
        utils.setup_metadata_controller()
    if app.argv.status_only:
        controllers.use('deploystatus').render()
    else:
        controllers.use('clouds').render()


def get_charmstore_bundles(spell, blessed):
    """searches charmstore, returns list of bundle metadata for bundles
    with tag 'conjure-$spell'
    """
    # We process multiple bundles here with our keyword search
    charmstore_results = charm.search(spell, blessed)
    # Check charmstore
    if charmstore_results['Total'] == 0:
        utils.warning("Could not find spells tagged 'conjure-{}'"
                      " in the Juju Charmstore.".format(spell))
        sys.exit(1)

    return charmstore_results['Results']


def apply_proxy():
    """ Sets up proxy information.
    """
    # Apply proxy information
    if app.argv.http_proxy:
        os.environ['HTTP_PROXY'] = app.argv.http_proxy
        os.environ['http_proxy'] = app.argv.http_proxy
    if app.argv.https_proxy:
        os.environ['HTTPS_PROXY'] = app.argv.https_proxy
        os.environ['https_proxy'] = app.argv.https_proxy


def main():
    opts = parse_options(sys.argv[1:])
    spell = os.path.basename(os.path.abspath(opts.spell))

    if not os.path.isdir(opts.cache_dir):
        os.makedirs(opts.cache_dir)

    app.fetcher = fetcher(opts.spell)

    if os.geteuid() == 0:
        utils.info("")
        utils.info("This should _not_ be run as root or with sudo.")
        utils.info("")
        sys.exit(1)

    # Application Config
    app.config = {'metadata': None}    
    app.argv = opts
    app.log = setup_logging("conjure-up/{}".format(spell),
                            os.path.join(opts.cache_dir, 'conjure-up.log'),
                            opts.debug)

    # Setup proxy
    apply_proxy()

    app.session_id = os.getenv('CONJURE_TEST_SESSION_ID',
                               '{}/{}'.format(
                                   spell,
                                   str(uuid.uuid4())))

    global_config_filename = app.argv.global_config_file
    if not os.path.exists(global_config_filename):
        # fallback to source tree location
        global_config_filename = os.path.join(os.path.dirname(__file__),
                                              "../etc/conjure-up.conf")
        if not os.path.exists(global_config_filename):
            utils.error("Could not find {}.".format(global_config_filename))
            sys.exit(1)

    with open(global_config_filename) as fp:
        global_conf = yaml.safe_load(fp.read())
        app.global_config = global_conf

    spells_dir = app.argv.spells_dir
    if not os.path.exists(spells_dir):
        spells_dir = os.path.join(os.path.dirname(__file__),
                                  "../spells")

    app.config['spells-dir'] = spells_dir
    spells_index_path = os.path.join(app.config['spells-dir'],
                                     'spells-index.yaml')
    with open(spells_index_path) as fp:
        app.spells_index = yaml.safe_load(fp.read())

    # Bind UI
    app.ui = ConjureUI()

    if app.fetcher is not None:
        utils.set_chosen_spell(spell, path.join(opts.cache_dir, spell))

        remote = get_remote_url(opts.spell)
        purge_top_level = True
        if remote is not None:

            if app.fetcher == "local":
                app.config['spell-dir'] = path.join(
                    opts.cache_dir,
                    os.path.basename(
                        os.path.abspath(spell)))
                download_local(remote, app.config['spell-dir'])

            else:
                download(remote, app.config['spell-dir'], purge_top_level)
        else:
            utils.warning("Could not find spell: {}".format(spell))
            sys.exit(1)

        utils.set_spell_metadata()
            
    if hasattr(app.argv, 'cloud'):
        if app.fetcher is not None:
            app.headless = True
            app.ui = None
        else:
            utils.error("Please specify a spell for headless mode.")
            sys.exit(1)

    if app.argv.status_only:
        if not juju.model_available():
            utils.error("Attempted to access the status screen without "
                        "an available Juju model.\n"
                        "Please select a model using 'juju switch' or "
                        "create a new controller using 'juju bootstrap'.")
            sys.exit(1)

    if app.headless:
        app.env['CONJURE_UP_HEADLESS'] = "1"
        _start()
    else:
        EventLoop.build_loop(app.ui, STYLES,
                             unhandled_input=unhandled_input)
        EventLoop.set_alarm_in(0.05, _start)
        EventLoop.run()


