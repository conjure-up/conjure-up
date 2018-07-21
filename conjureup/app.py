""" Application entrypoint
"""

import argparse
import asyncio
import os
import os.path as path
import pathlib
import platform
import signal
import subprocess
import sys
import textwrap
import uuid

import raven
import yaml
from juju.model import CharmStore
from kv import KV
from prettytable import PrettyTable
from raven.transport.requests import RequestsHTTPTransport
from termcolor import colored
from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES

from conjureup import __version__ as VERSION
from conjureup import charm, consts, controllers, errors, events, juju, utils
from conjureup.app_config import app
from conjureup.download import (
    EndpointType,
    detect_endpoint,
    download,
    download_local,
    download_or_sync_registry,
    get_remote_url
)
from conjureup.log import setup_logging
from conjureup.models.addon import AddonModel
from conjureup.models.conjurefile import Conjurefile
from conjureup.models.provider import load_schema
from conjureup.models.step import StepModel
from conjureup.telemetry import SENTRY_DSN, track_event, track_screen
from conjureup.ui import ConjureUI


def parse_options(argv):
    parser = argparse.ArgumentParser(prog="conjure-up")
    parser.add_argument('spell', nargs='?',
                        default=consts.UNSPECIFIED_SPELL,
                        help="""The name ('openstack-nclxd') or location
                        ('githubusername/spellrepo') of a conjure-up
                        spell, or a keyword matching multiple spells
                        ('openstack')""")
    parser.add_argument('-d', '--debug', action='store_true',
                        dest='debug', default=False,
                        help='Enable debug logging.')
    parser.add_argument('--show-env', action='store_true',
                        dest='show_env',
                        help='Shows what environment variables are used '
                        'during post deployment actions. This is useful '
                        'for headless installs allowing you to set those '
                        'variables to further customize your deployment.')
    parser.add_argument('--registry', dest='registry',
                        help='Spells Registry',
                        default='https://github.com/conjure-up/spells.git')
    parser.add_argument('-b', '--branch', '--registry-branch',
                        dest='registry_branch',
                        help='Branch to use on the spells registry',
                        default=os.getenv('CONJUREUP_REGISTRY_BRANCH',
                                          'master'))
    parser.add_argument('--cache-dir', dest='cache_dir',
                        help='Download directory for spells',
                        default=os.path.expanduser("~/.cache/conjure-up"))
    parser.add_argument('--spells-dir', dest='spells_dir',
                        help='Location of conjure-up managed spells directory',
                        default=os.path.expanduser(
                            "~/.cache/conjure-up-spells"))
    parser.add_argument('-c', '--conf-file', dest='conf_file',
                        help='Path to configuration file', action='append',
                        type=pathlib.Path)
    parser.add_argument('--apt-proxy', dest='apt_http_proxy',
                        help='Specify APT proxy')
    parser.add_argument('--apt-https-proxy', dest='apt_https_proxy',
                        help='Specify APT HTTPS proxy')
    parser.add_argument('--http-proxy', dest='http_proxy',
                        help='Specify HTTP proxy')
    parser.add_argument('--https-proxy', dest='https_proxy',
                        help='Specify HTTPS proxy')
    parser.add_argument('--no-proxy', dest='no_proxy',
                        help='Comma separated list of IPs to not '
                        'filter through a proxy')
    parser.add_argument('--bootstrap-timeout', dest='bootstrap_timeout',
                        help='Amount of time to wait for initial controller '
                        'creation. Useful for slower network connections.')
    parser.add_argument('--bootstrap-to', dest='bootstrap_to',
                        help='The MAAS node hostname to deploy to. Useful '
                        'for using lower end hardware as the Juju admin '
                        'controller.', metavar='<host>.maas')
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('--no-track', '--notrack', action='store_true',
                        dest='no_track',
                        help='Opt out of sending anonymous usage '
                        'information to Canonical.')
    parser.add_argument('--no-report', '--noreport', action='store_true',
                        dest='no_report',
                        help='Opt out of sending anonymous error reports '
                        'to Canonical.')
    parser.add_argument('--no-sync', '--nosync', action='store_true',
                        dest='no_sync', default=False,
                        help='Opt out of syncing with spells '
                        'registry.')
    parser.add_argument('--sync', action='store_false',
                        dest='no_sync', default=False,
                        help='Re-enable syncing with spells '
                        'registry, if disabled with --no-sync.')
    parser.add_argument('--color', type=str, default='auto',
                        choices=['auto', 'never', 'always'],
                        help='Whether to use colorized output '
                             'in headless mode.')
    parser.add_argument('--bundle-add', type=pathlib.Path,
                        help="Path to a bundle fragment file which will be "
                             "merged with the spell's bundle")
    parser.add_argument('--bundle-remove', type=pathlib.Path,
                        help="Path to a bundle fragment file which will be "
                             "subtracted from the spell's bundle")
    parser.add_argument('--gen-config', action='store_true',
                        dest='gen_config',
                        help='Prints a skeleton Conjurefile to stdout')
    parser.add_argument('--destroy', action='store_true',
                        dest='destroy',
                        help='Interface to uninstall '
                        'deployments, used with `conjure-down`')

    # Channels
    parser.add_argument('--channel', type=str,
                        choices=charm.CHANNELS,
                        dest='channel',
                        default='stable',
                        help='conjure-up spell from a release channel')

    parser.add_argument('cloud', nargs='?',
                        help="Name of a Juju cloud to "
                        "target, such as ['aws', 'localhost' ...], optionally "
                        "with a region, in the form <cloud>/<region>. "
                        "If no controller exists there, one may be created")
    parser.add_argument('controller', nargs='?',
                        help="Name of a juju controller to target. "
                        "If not provided, a new one is created.")
    parser.add_argument('model', nargs='?',
                        help="Name of a juju model to target. "
                        "If not provided, a new one is created.")
    return parser.parse_args(argv)


async def _start(*args, **kwargs):
    # NB: we have to set the exception handler here because we need to
    # override the one set by urwid, which happens in MainLoop.run()
    app.loop.set_exception_handler(events.handle_exception)

    if app.conjurefile['destroy']:
        track_screen('Destroy Deployment Start')
        controllers.use('destroy').render()
        return

    track_screen("Application Start")
    track_event("OS", platform.platform(), "")

    if app.endpoint_type in [None, EndpointType.LOCAL_SEARCH]:
        controllers.use('spellpicker').render()
        return

    controllers.setup_metadata_controller()

    if app.headless:
        controllers.use('clouds').render()
    elif app.selected_addons:
        controllers.use('clouds').render()
    else:
        controllers.use('addons').render()


def apply_proxy():
    """ Sets up proxy information.
    """
    # Apply proxy information
    if app.conjurefile['http-proxy']:
        os.environ['HTTP_PROXY'] = app.conjurefile['http-proxy']
        os.environ['http_proxy'] = app.conjurefile['http-proxy']
    if app.conjurefile['https-proxy']:
        os.environ['HTTPS_PROXY'] = app.conjurefile['https-proxy']
        os.environ['https_proxy'] = app.conjurefile['https-proxy']


def show_env():
    """ Shows environment variables from post deploy actions
    """
    print("Available environment variables: \n")
    table = PrettyTable()
    table.field_names = ["ENV", "DEFAULT", ""]
    table.align = 'l'
    for step in app.steps:
        for x in step.additional_input:
            default = colored(x.get('default', ''), 'green', attrs=['bold'])
            key = colored(x['key'], 'blue', attrs=['bold'])
            table.add_row([key, default,
                           textwrap.fill(step.description, width=55)])
    print(table)
    print("")

    url = ("https://docs.ubuntu.com/conjure-up/"
           "en/usage#customising-headless-mode")
    print(
        textwrap.fill(
            "See {} for more information on using these variables to further "
            "customize your deployment.".format(url), width=79))
    sys.exit(0)


def main():
    if os.geteuid() == 0:
        print("")
        print("  !! This should _not_ be run as root or with sudo. !!")
        print("")
        sys.exit(1)

    # Verify we can access ~/.local/share/juju if it exists
    juju_dir = pathlib.Path('~/.local/share/juju').expanduser()
    if juju_dir.exists():
        try:
            for f in juju_dir.iterdir():
                if f.is_file():
                    f.read_text()
        except PermissionError:
            print("")
            print("  !! Unable to read from ~/.local/share/juju, please "
                  "double check your permissions on that directory "
                  "and its files. !!")
            print("")
            sys.exit(1)

    utils.set_terminal_title("conjure-up")
    opts = parse_options(sys.argv[1:])
    opt_defaults = parse_options([])

    # Load conjurefile, merge any overridding options from argv
    if not opts.conf_file:
        opts.conf_file = []
    if pathlib.Path('~/.config/conjure-up.conf').expanduser().exists():
        opts.conf_file.insert(
            0, pathlib.Path('~/.config/conjure-up.conf').expanduser())
    if (pathlib.Path('.') / 'Conjurefile').exists():
        opts.conf_file.insert(0, pathlib.Path('.') / 'Conjurefile')
    for conf in opts.conf_file:
        if not conf.exists():
            print("Unable to locate config {} for processing.".format(
                str(conf)))
            sys.exit(1)

    try:
        app.conjurefile = Conjurefile.load(opts.conf_file)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    app.conjurefile.merge_argv(opts, opt_defaults)

    if app.conjurefile['gen-config']:
        Conjurefile.print_tpl()
        sys.exit(0)

    spell = os.path.basename(os.path.abspath(app.conjurefile['spell']))

    if not os.path.isdir(app.conjurefile['cache-dir']):
        os.makedirs(app.conjurefile['cache-dir'])

    # Application Config
    kv_db = os.path.join(app.conjurefile['cache-dir'], '.state.db')
    app.state = KV(kv_db)

    app.env = os.environ.copy()
    app.env['KV_DB'] = kv_db
    app.config = {'metadata': None}

    app.log = setup_logging(app,
                            os.path.join(app.conjurefile['cache-dir'],
                                         'conjure-up.log'),
                            app.conjurefile.get('debug', False))

    # Make sure juju paths are setup
    juju.set_bin_path()
    juju.set_wait_path()

    app.no_track = app.conjurefile['no-track']
    app.no_report = app.conjurefile['no-report']

    # Grab current LXD and Juju versions
    app.log.debug("Juju version: {}, "
                  "conjure-up version: {}".format(
                      utils.juju_version(),
                      VERSION))

    # Setup proxy
    apply_proxy()

    app.session_id = os.getenv('CONJURE_TEST_SESSION_ID',
                               str(uuid.uuid4()))

    spells_dir = app.conjurefile['spells-dir']

    app.config['spells-dir'] = spells_dir
    spells_index_path = os.path.join(app.config['spells-dir'],
                                     'spells-index.yaml')

    if not app.conjurefile['no-sync']:
        if not os.path.exists(spells_dir):
            utils.info("No spells found, syncing from registry, please wait.")
        try:
            download_or_sync_registry(
                app.conjurefile['registry'],
                spells_dir, branch=app.conjurefile['registry-branch'])
        except subprocess.CalledProcessError as e:
            if not os.path.exists(spells_dir):
                utils.error("Could not load from registry")
                sys.exit(1)

            app.log.debug(
                'Could not sync spells from github: {}'.format(e))
    else:
        if not os.path.exists(spells_index_path):
            utils.error(
                "You opted to not sync from the spells registry, however, "
                "we could not find any suitable spells in: "
                "{}".format(spells_dir))
            sys.exit(1)

    with open(spells_index_path) as fp:
        app.spells_index = yaml.safe_load(fp.read())

    addons_aliases_index_path = os.path.join(app.config['spells-dir'],
                                             'addons-aliases.yaml')
    if os.path.exists(addons_aliases_index_path):
        with open(addons_aliases_index_path) as fp:
            app.addons_aliases = yaml.safe_load(fp.read())

    spell_name = spell
    app.endpoint_type = detect_endpoint(app.conjurefile['spell'])

    if app.conjurefile['spell'] != consts.UNSPECIFIED_SPELL:
        app.spell_given = True

    # Check if spell is actually an addon
    addon = utils.find_addons_matching(app.conjurefile['spell'])
    if addon:
        app.log.debug("addon found, setting required spell")
        utils.set_chosen_spell(addon['spell'],
                               os.path.join(app.conjurefile['cache-dir'],
                                            addon['spell']))
        download_local(os.path.join(app.config['spells-dir'],
                                    addon['spell']),
                       app.config['spell-dir'])
        utils.set_spell_metadata()
        StepModel.load_spell_steps()
        AddonModel.load_spell_addons()
        app.selected_addons = addon['addons']
        app.alias_given = True
        controllers.setup_metadata_controller()
        app.endpoint_type = EndpointType.LOCAL_DIR

    elif app.endpoint_type == EndpointType.LOCAL_SEARCH:
        spells = utils.find_spells_matching(app.conjurefile['spell'])

        if len(spells) == 0:
            utils.error("Can't find a spell matching '{}'".format(
                app.conjurefile['spell']))
            sys.exit(1)

        # One result means it was a direct match and we can copy it
        # now. Changing the endpoint type then stops us from showing
        # the picker UI. More than one result means we need to show
        # the picker UI and will defer the copy to
        # SpellPickerController.finish(), so nothing to do here.
        if len(spells) == 1:
            app.log.debug("found spell {}".format(spells[0][1]))
            spell = spells[0][1]
            utils.set_chosen_spell(spell_name,
                                   os.path.join(app.conjurefile['cache-dir'],
                                                spell['key']))
            download_local(os.path.join(app.config['spells-dir'],
                                        spell['key']),
                           app.config['spell-dir'])
            utils.set_spell_metadata()
            StepModel.load_spell_steps()
            AddonModel.load_spell_addons()
            app.endpoint_type = EndpointType.LOCAL_DIR

    # download spell if necessary
    elif app.endpoint_type == EndpointType.LOCAL_DIR:
        if not os.path.isdir(app.conjurefile['spell']):
            utils.warning("Could not find spell {}".format(
                app.conjurefile['spell']))
            sys.exit(1)

        if not os.path.exists(os.path.join(app.conjurefile['spell'],
                                           "metadata.yaml")):
            utils.warning("'{}' does not appear to be a spell. "
                          "{}/metadata.yaml was not found.".format(
                              app.conjurefile['spell'],
                              app.conjurefile['spell']))
            sys.exit(1)

        spell_name = os.path.basename(os.path.abspath(spell))
        utils.set_chosen_spell(spell_name,
                               path.join(app.conjurefile['cache-dir'],
                                         spell_name))
        download_local(app.conjurefile['spell'], app.config['spell-dir'])
        utils.set_spell_metadata()
        StepModel.load_spell_steps()
        AddonModel.load_spell_addons()

    elif app.endpoint_type in [EndpointType.VCS, EndpointType.HTTP]:

        utils.set_chosen_spell(spell, path.join(
            app.conjurefile['cache-dir'], spell))
        remote = get_remote_url(app.conjurefile['spell'])

        if remote is None:
            utils.warning("Can't guess URL matching '{}'".format(
                app.conjurefile['spell']))
            sys.exit(1)

        download(remote, app.config['spell-dir'], True)
        utils.set_spell_metadata()
        StepModel.load_spell_steps()
        AddonModel.load_spell_addons()

    app.env['CONJURE_UP_CACHEDIR'] = app.conjurefile['cache-dir']
    app.env['PATH'] = "/snap/bin:{}".format(app.env['PATH'])

    if app.conjurefile['show-env']:
        if app.endpoint_type in [None, EndpointType.LOCAL_SEARCH]:
            utils.error("Please specify a spell for headless mode.")
            sys.exit(1)

        show_env()

    app.sentry = raven.Client(
        dsn=SENTRY_DSN,
        release=VERSION,
        transport=RequestsHTTPTransport,
        processors=(
            'conjureup.utils.SanitizeDataProcessor',
        )
    )

    app.loop = asyncio.get_event_loop()
    app.loop.add_signal_handler(signal.SIGINT, events.Shutdown.set)

    # Enable charmstore querying
    app.juju.charmstore = CharmStore(app.loop)
    try:
        if app.conjurefile.is_valid:
            cloud = None
            region = None
            if '/' in app.conjurefile['cloud']:
                parse_cli_cloud = app.conjurefile['cloud'].split('/')
                cloud, region = parse_cli_cloud
                app.log.debug(
                    "Region found {} for cloud {}".format(cloud,
                                                          region))
            else:
                cloud = app.conjurefile['cloud']

            cloud_types = juju.get_cloud_types_by_name()
            if cloud not in cloud_types:
                utils.error('Unknown cloud: {}'.format(cloud))
                sys.exit(1)

            if app.endpoint_type in [None, EndpointType.LOCAL_SEARCH]:
                utils.error("Please specify a spell for headless mode.")
                sys.exit(1)

            app.provider = load_schema(cloud_types[cloud])

            try:
                app.provider.load(cloud)
            except errors.SchemaCloudError as e:
                utils.error(e)
                sys.exit(1)

            if region:
                app.provider.region = region

            app.headless = True
            app.ui = None
            app.env['CONJURE_UP_HEADLESS'] = "1"
            app.loop.create_task(events.shutdown_watcher())
            app.loop.create_task(_start())
            app.loop.run_forever()

        else:
            app.ui = ConjureUI()
            app.ui.set_footer('Press ? for help')

            EventLoop.build_loop(app.ui, STYLES,
                                 unhandled_input=events.unhandled_input,
                                 handle_mouse=False)
            app.loop.create_task(events.shutdown_watcher())
            app.loop.create_task(_start())
            EventLoop.run()
    finally:
        # explicitly close asyncio event loop to avoid hitting the
        # following issue due to signal handlers added by
        # asyncio.create_subprocess_exec being cleaned up during final
        # garbage collection: https://github.com/python/asyncio/issues/396
        app.loop.close()
    sys.exit(app.exit_code)
