""" Application entrypoint
"""

from conjure import __version__ as VERSION
from conjure import async
from conjure import controllers
from conjure import juju
from conjure import utils
from conjure import charm
from conjure.app_config import app
from conjure.download import download, get_remote_url, fetcher
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
        controllers.use('deploystatus').render()
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
                "Only Juju v2 and above is supported, "
                "your currently installed version is {}.\n\n"
                "Please refer to {} for help on installing "
                "the correct Juju.".format(juju_version, docs_url))
            sys.exit(1)
    except Exception as e:
        utils.warning(e)
        sys.exit(1)


def install_curated_spell(spell):
    """ Installs the debian package associated with curated spell
    """
    if not utils.check_deb_installed(spell):
        os.execl("/usr/share/conjure-up/do-apt-install",
                 "/usr/share/conjure-up/do-apt-install",
                 spell)


def load_charmstore_results(spell, blessed):
    """ Loads results from charmstore
    """
    # We process multiple bundles here with our keyword search
    charmstore_results = charm.search(spell, blessed)
    # Check charmstore
    if charmstore_results['Total'] == 0:
        utils.warning('Could not find spell in charmstore.')
        sys.exit(1)

    return charmstore_results['Results']


def main():
    opts = parse_options(sys.argv[1:])
    if "/" in opts.spell:
        spell = opts.spell.split("/")[-1]
    else:
        spell = opts.spell

    app.fetcher = fetcher(opts.spell)

    if os.geteuid() == 0:
        utils.info("")
        utils.info("This should _not_ be run as root or with sudo.")
        utils.info("")
        sys.exit(1)

    has_valid_juju()

    # Application Config
    app.argv = opts
    app.log = setup_logging("conjure-up/{}".format(spell),
                            opts.debug)
    app.session_id = os.getenv('CONJURE_TEST_SESSION_ID',
                               '{}/{}'.format(
                                   spell,
                                   str(uuid.uuid4())))

    global_conf_file = '/etc/conjure-up.conf'
    if not os.path.exists(global_conf_file):
        global_conf_file = os.path.join(
            os.path.dirname(__file__), '..', 'etc', 'conjure-up.conf')
    with open(global_conf_file) as fp:
        global_conf = yaml.safe_load(fp.read())

    # Bind UI
    app.ui = ConjureUI()

    if spell in global_conf['curated_spells']:
        install_curated_spell(spell)

    spell_dir = os.environ.get('XDG_CACHE_HOME', os.path.join(
        os.path.expanduser('~'),
        '.cache/conjure-up'))

    if app.fetcher == "charmstore":
        app.bundles = load_charmstore_results(spell, global_conf['blessed'])
        app.config = {'metadata': None,
                      'spell-dir': spell_dir,
                      'spell': spell}

        # Set a general description of spell
        if path.isfile('/usr/share/conjure-up/keyword-definitions.yaml'):
            with open('/usr/share/conjure-up/keyword-definitions.yaml') as fp:
                definitions = yaml.safe_load(fp.read())
        try:
            app.config['description'] = definitions[spell]
        except:
            utils.warning(
                "Failed to find a description for spell: {}, "
                "and is a bug that should be filed.".format(spell))

    else:
        # Check cache dir for spells
        spell_dir = path.join(spell_dir, spell)

        metadata_path = path.join(spell_dir,
                                  'conjure/metadata.json')

        remote = get_remote_url(opts.spell)
        purge_top_level = True
        if remote is not None:
            if app.fetcher == "charmstore" or \
               app.fetcher == "charmstore-direct":
                purge_top_level = False
            download(remote, spell_dir, purge_top_level)
        else:
            utils.warning("Could not find spell: {}".format(spell))
            sys.exit(1)

        with open(metadata_path) as fp:
            metadata = json.load(fp)

        app.config = {'metadata': metadata,
                      'spell-dir': spell_dir,
                      'spell': spell}

        # Need to provide app.bundles dictionary even for single
        # spells in the GUI
        app.bundles = [
            {
                'Meta': {
                    'extra-info/conjure': metadata
                }
            }
        ]

    if hasattr(app.argv, 'cloud'):
        if app.fetcher != "charmstore":
            app.headless = True
            app.ui = None
        else:
            utils.error("Unable run a keyword search in headless mode, "
                        "please provide a single bundle path.")
            sys.exit(1)

    app.env = os.environ.copy()
    app.env['CONJURE_UP_SPELL'] = spell

    if app.headless:
        app.env['CONJURE_UP_HEADLESS'] = "1"
        _start()
    else:
        EventLoop.build_loop(app.ui, STYLES,
                             unhandled_input=unhandled_input)
        EventLoop.set_alarm_in(0.05, _start)
        EventLoop.run()
