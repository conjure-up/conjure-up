""" Application entrypoint
"""

from conjure import __version__ as VERSION
from conjure import async
from conjure import controllers
from conjure import juju
from conjure import utils
from conjure import charm
from conjure.app_config import app
from conjure.download import (download, download_local,
                              get_remote_url, fetcher)
from conjure.log import setup_logging
from conjure.ui import ConjureUI
from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES
import argparse
import json
import os
import os.path as path
import sys
import uuid
import yaml
import re


def parse_options(argv):
    parser = argparse.ArgumentParser(prog="conjure-up")
    parser.add_argument('spell', help="Specify the solution to "
                        "conjure, e.g. openstack")
    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug',
                        help='Enable debug logging.')
    parser.add_argument('-s', '--status', action='store_true',
                        dest='status_only',
                        help='Display the summary of the conjuring')
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
    """ Initially load cloud selection screen
    """
    if app.argv.status_only:
        controllers.use('summary').render()
    else:
        controllers.use('clouds').render()


def has_valid_juju():
    """ Checks for valid Juju version
    """
    try:
        docs_url = "https://jujucharms.com/docs/stable/getting-started"
        juju_version = juju.version()
        if int(juju_version[0]) < 2:
            utils.warning(
                "Only Juju v2 beta9 and above is supported, "
                "your currently installed version is {}.\n\n"
                "Please refer to {} for help on installing "
                "the correct Juju.".format(juju_version, docs_url))
            sys.exit(1)

        beta_release_regex = re.compile('^.*beta(\d+)')
        beta_release_ver = beta_release_regex.search(juju_version)
        if beta_release_ver is not None:
            app.log.debug("Beta release found, checking minimum requirements.")
            if int(beta_release_ver.group(1)) < 10:
                utils.warning(
                    "Juju v2 beta10 is the lowest support release. Please "
                    "make sure you are on the latest release Juju. See {} "
                    "for more information.".format(docs_url)
                )
                sys.exit(1)
    except Exception as e:
        utils.warning(e)
        sys.exit(1)


def install_pkgs(pkgs):
    """ Installs the debian package associated with curated spell
    """
    if not isinstance(pkgs, list):
        pkgs = [pkgs]

    all_debs_installed = all(utils.check_deb_installed(x) for x
                             in pkgs)
    if not all_debs_installed:
        utils.info(
            "Installing additional required packages: {}".format(
                " ".join(pkgs)))
        os.execl("/usr/share/conjure-up/do-apt-install",
                 "/usr/share/conjure-up/do-apt-install",
                 " ".join(pkgs))


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

    # cached spell dir
    spell_dir = os.environ.get('XDG_CACHE_HOME', os.path.join(
        os.path.expanduser('~'),
        '.cache/conjure-up'))

    app.fetcher = fetcher(opts.spell)

    if os.geteuid() == 0:
        utils.info("")
        utils.info("This should _not_ be run as root or with sudo.")
        utils.info("")
        sys.exit(1)

    # Application Config
    app.argv = opts
    app.log = setup_logging("conjure-up/{}".format(spell),
                            opts.debug)

    # Setup proxy
    apply_proxy()

    app.session_id = os.getenv('CONJURE_TEST_SESSION_ID',
                               '{}/{}'.format(
                                   spell,
                                   str(uuid.uuid4())))

    has_valid_juju()

    global_conf_file = '/etc/conjure-up.conf'
    if not os.path.exists(global_conf_file):
        global_conf_file = os.path.join(
            os.path.dirname(__file__), '..', 'etc', 'conjure-up.conf')
    with open(global_conf_file) as fp:
        global_conf = yaml.safe_load(fp.read())

    # Bind UI
    app.ui = ConjureUI()

    if app.fetcher == "charmstore-search":
        utils.info("Loading current {} spells "
                   "from Juju Charmstore, please wait.".format(spell))
        app.bundles = get_charmstore_bundles(spell, global_conf['blessed'])
        app.config = {'metadata': None,
                      'spell-dir': spell_dir,
                      'spell': spell}

        # Set a general description of spell
        definition = None
        if path.isfile('/usr/share/conjure-up/keyword-definitions.yaml'):
            with open('/usr/share/conjure-up/keyword-definitions.yaml') as fp:
                definitions = yaml.safe_load(fp.read())
                definition = definitions.get(spell, None)
        if definition is None:
            try:
                definition = next(
                    bundle['Meta']['bundle-metadata']['Description']
                    for bundle in app.bundles if 'Description'
                    in bundle['Meta']['bundle-metadata'])
            except StopIteration:
                app.log.error("Could not find a suitable description "
                              "for spell: {}".format(spell))

        if definition is not None:
            app.config['description'] = definition
        else:
            utils.warning(
                "Failed to find a description for spell: {}, "
                "and is a bug that should be filed.".format(spell))

        # Install any required packages for any of the bundles
        for bundle in app.bundles:
            extra_info = bundle['Meta']['extra-info/conjure-up']
            if 'packages' in extra_info:
                app.log.debug('Found {} to install via apt'.format(
                    extra_info['packages']))
                install_pkgs(extra_info['packages'])

    else:
        app.config = {'metadata': None,
                      'spell-dir': path.join(spell_dir, spell),
                      'spell': spell}

        remote = get_remote_url(opts.spell)
        purge_top_level = True
        if remote is not None:

            metadata_path = path.join(app.config['spell-dir'],
                                      'conjure/metadata.json')

            if app.fetcher == "local":
                app.config['spell-dir'] = path.join(
                    spell_dir,
                    os.path.basename(
                        os.path.abspath(spell)))
                metadata_path = path.join(app.config['spell-dir'],
                                          'conjure/metadata.json')
                download_local(remote, app.config['spell-dir'])

            else:
                if app.fetcher == "charmstore-search" or \
                   app.fetcher == "charmstore-direct":
                    purge_top_level = False
                download(remote, app.config['spell-dir'], purge_top_level)
        else:
            utils.warning("Could not find spell: {}".format(spell))
            sys.exit(1)

        with open(metadata_path) as fp:
            metadata = json.load(fp)

        app.config['metadata'] = metadata
        if app.config['metadata'].get('packages', None):
            install_pkgs(app.config['metadata']['packages'])

        # Need to provide app.bundles dictionary even for single
        # spells in the GUI
        app.bundles = [
            {
                'Meta': {
                    'extra-info/conjure-up': metadata
                }
            }
        ]

    if hasattr(app.argv, 'cloud'):
        if app.fetcher != "charmstore-search":
            app.headless = True
            app.ui = None
        else:
            utils.error("Unable run a keyword search in headless mode, "
                        "please provide a single bundle path.")
            sys.exit(1)

    app.env = os.environ.copy()
    app.env['CONJURE_UP_SPELL'] = spell

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
