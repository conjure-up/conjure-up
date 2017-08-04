""" Application entrypoint
"""

import argparse
import asyncio
import configparser
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
import redis
import yaml
from prettytable import PrettyTable
from raven.transport.requests import RequestsHTTPTransport
from termcolor import colored
from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES

from conjureup import __version__ as VERSION
from conjureup import charm, consts, controllers, events, juju, utils
from conjureup.app_config import app
from conjureup.controllers.showsteps.common import load_steps
from conjureup.download import (
    EndpointType,
    detect_endpoint,
    download,
    download_local,
    download_or_sync_registry,
    get_remote_url
)
from conjureup.log import setup_logging
from conjureup.models.provider import SchemaErrorUnknownCloud, load_schema
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
    parser.add_argument('--cache-dir', dest='cache_dir',
                        help='Download directory for spells',
                        default=os.path.expanduser("~/.cache/conjure-up"))
    parser.add_argument('--spells-dir', dest='spells_dir',
                        help='Location of conjure-up managed spells directory',
                        default=os.path.expanduser(
                            "~/.cache/conjure-up-spells"))
    parser.add_argument('--conf-file', dest='conf_file',
                        help='Path to configuration file', type=pathlib.Path,
                        default=pathlib.Path("~/.config/conjure-up.conf"))
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
    parser.add_argument('--redis-port', dest='redis_port',
                        help='Redis port to connect to',
                        default=6379)
    parser.add_argument(
        '--version', action='version', version='%(prog)s {}'.format(VERSION))
    parser.add_argument('--notrack', action='store_true',
                        dest='notrack',
                        help='Opt out of sending anonymous usage '
                        'information to Canonical.')
    parser.add_argument('--noreport', action='store_true',
                        dest='noreport',
                        help='Opt out of sending anonymous error reports '
                        'to Canonical.')
    parser.add_argument('--nosync', action='store_true',
                        dest='nosync',
                        help='Opt out of syncing with spells '
                        'registry.')

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

    if app.endpoint_type in [None, EndpointType.LOCAL_SEARCH]:
        controllers.use('spellpicker').render()
        return

    utils.setup_metadata_controller()

    controllers.use('clouds').render()


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


def show_env():
    """ Shows environment variables from post deploy actions
    """
    load_steps()
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
    spell = os.path.basename(os.path.abspath(opts.spell))

    if not os.path.isdir(opts.cache_dir):
        os.makedirs(opts.cache_dir)

    # Application Config
    app.state = redis.StrictRedis(host='localhost',
                                  port=opts.redis_port,
                                  db=0)
    # confirm that the Redis connection is working
    # XXX perhaps we should start the service if not running
    try:
        app.state.get('test')
    except redis.exceptions.ConnectionError:
        print("")
        print("  !! Unable to connect to Redis. !!")
        print("")
        sys.exit(1)
    app.env = os.environ.copy()
    app.config = {'metadata': None}
    app.argv = opts
    app.log = setup_logging(app,
                            os.path.join(opts.cache_dir, 'conjure-up.log'),
                            opts.debug)

    if app.argv.conf_file.expanduser().exists():
        conf = configparser.ConfigParser()
        conf.read_string(app.argv.conf_file.expanduser().read_text())
        app.notrack = conf.getboolean('REPORTING', 'notrack', fallback=False)
        app.noreport = conf.getboolean('REPORTING', 'noreport', fallback=False)
    if app.argv.notrack:
        app.notrack = True
    if app.argv.noreport:
        app.noreport = True

    # Grab current LXD and Juju versions
    app.log.debug("LXD version: {}, "
                  "Juju version: {}, "
                  "conjure-up version: {}".format(
                      utils.lxd_version(),
                      utils.juju_version(),
                      VERSION))

    # Setup proxy
    apply_proxy()

    app.session_id = os.getenv('CONJURE_TEST_SESSION_ID',
                               str(uuid.uuid4()))

    spells_dir = app.argv.spells_dir

    app.config['spells-dir'] = spells_dir
    spells_index_path = os.path.join(app.config['spells-dir'],
                                     'spells-index.yaml')
    spells_registry_branch = os.getenv('CONJUREUP_REGISTRY_BRANCH', 'stable')

    if not app.argv.nosync:
        if not os.path.exists(spells_dir):
            utils.info("No spells found, syncing from registry, please wait.")
        try:
            download_or_sync_registry(
                app.argv.registry,
                spells_dir, branch=spells_registry_branch)
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

    spell_name = spell
    app.endpoint_type = detect_endpoint(opts.spell)

    if app.endpoint_type == EndpointType.LOCAL_SEARCH:
        spells = utils.find_spells_matching(opts.spell)

        if len(spells) == 0:
            utils.error("Can't find a spell matching '{}'".format(opts.spell))
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
                                   os.path.join(opts.cache_dir,
                                                spell['key']))
            download_local(os.path.join(app.config['spells-dir'],
                                        spell['key']),
                           app.config['spell-dir'])
            utils.set_spell_metadata()
            app.endpoint_type = EndpointType.LOCAL_DIR

    # download spell if necessary
    elif app.endpoint_type == EndpointType.LOCAL_DIR:
        if not os.path.isdir(opts.spell):
            utils.warning("Could not find spell {}".format(opts.spell))
            sys.exit(1)

        if not os.path.exists(os.path.join(opts.spell,
                                           "metadata.yaml")):
            utils.warning("'{}' does not appear to be a spell. "
                          "{}/metadata.yaml was not found.".format(
                              opts.spell, opts.spell))
            sys.exit(1)

        spell_name = os.path.basename(os.path.abspath(spell))
        utils.set_chosen_spell(spell_name,
                               path.join(opts.cache_dir, spell_name))
        download_local(opts.spell, app.config['spell-dir'])
        utils.set_spell_metadata()

    elif app.endpoint_type in [EndpointType.VCS, EndpointType.HTTP]:

        utils.set_chosen_spell(spell, path.join(opts.cache_dir, spell))
        remote = get_remote_url(opts.spell)

        if remote is None:
            utils.warning("Can't guess URL matching '{}'".format(opts.spell))
            sys.exit(1)

        download(remote, app.config['spell-dir'], True)
        utils.set_spell_metadata()

    app.env['CONJURE_UP_CACHEDIR'] = app.argv.cache_dir

    if app.argv.show_env:
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

    track_screen("Application Start")
    track_event("OS", platform.platform(), "")

    app.loop = asyncio.get_event_loop()
    app.loop.add_signal_handler(signal.SIGINT, events.Shutdown.set)
    try:
        if app.argv.cloud:
            cloud = None
            region = None
            if '/' in app.argv.cloud:
                parse_cli_cloud = app.argv.cloud.split('/')
                cloud, region = parse_cli_cloud
                app.log.debug(
                    "Region found {} for cloud {}".format(app.cloud,
                                                          app.region))
            else:
                cloud = app.argv.cloud

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
            except SchemaErrorUnknownCloud as e:
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

            EventLoop.build_loop(app.ui, STYLES,
                                 unhandled_input=events.unhandled_input)
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
