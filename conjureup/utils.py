import asyncio
import codecs
import errno
import json
import logging
import os
import pty
import re
import shutil
import socket
import subprocess
import sys
import uuid
from collections import Mapping
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from subprocess import PIPE, Popen, check_call, check_output

import aiofiles
import yaml
from bundleplacer.bundle import Bundle
from bundleplacer.charmstore_api import MetadataController
from bundleplacer.config import Config
from pkg_resources import parse_version
from raven.processors import SanitizePasswordsProcessor
from termcolor import cprint

from conjureup import charm
from conjureup.app_config import app
from conjureup.telemetry import track_event


@contextmanager
def chdir(directory):
    """Change the current working directory to a different directory for a code
    block and return the previous directory after the block exits. Useful to
    run commands from a specificed directory.

    :param str directory: The directory path to change to for this context.
    """
    cur = os.getcwd()
    try:
        yield os.chdir(directory)
    finally:
        os.chdir(cur)


def run(cmd, **kwargs):
    """ Compatibility function to support python 3.4
    """
    try:
        from subprocess import run as _run
        return _run(cmd, **kwargs)
    except ImportError:
        if 'check' in kwargs:
            del kwargs['check']
            return check_call(cmd, **kwargs)
        else:
            return check_output(cmd, **kwargs)


def run_script(path, stderr=PIPE, stdout=PIPE):
    return run(path, shell=True, stderr=stderr, stdout=stdout, env=app.env)


def run_attach(cmd, output_cb=None):
    """ run command and attach output to cb

    Arguments:
    cmd: shell command
    output_cb: where to display output
    """

    stdoutmaster, stdoutslave = pty.openpty()
    subproc = Popen(cmd, shell=True,
                    stdout=stdoutslave,
                    stderr=PIPE)
    os.close(stdoutslave)
    decoder = codecs.getincrementaldecoder('utf-8')()

    def last_ten_lines(s):
        chunk = s[-1500:]
        lines = chunk.splitlines(True)
        return ''.join(lines[-10:]).replace('\r', '')

    decoded_output = ""
    try:
        while subproc.poll() is None:
            try:
                b = os.read(stdoutmaster, 512)
            except OSError as e:
                if e.errno != errno.EIO:
                    raise
                break
            else:
                final = False
                if not b:
                    final = True
                decoded_chars = decoder.decode(b, final)
                if decoded_chars is None:
                    continue

                decoded_output += decoded_chars
                if output_cb:
                    ls = last_ten_lines(decoded_output)

                    output_cb(ls)
                if final:
                    break
    finally:
        os.close(stdoutmaster)
        if subproc.poll() is None:
            subproc.kill()
        subproc.wait()

    errors = [l.decode('utf-8') for l in subproc.stderr.readlines()]
    if output_cb:
        output_cb(last_ten_lines(decoded_output))

    errors = ''.join(errors)

    if subproc.returncode == 0:
        return decoded_output.strip()
    else:
        raise Exception("Problem running {0} "
                        "{1}:{2}".format(cmd,
                                         subproc.returncode))


async def arun(cmd, input=None, check=False, env=None, encoding='utf8',
               stdin=subprocess.PIPE, stdout=subprocess.PIPE,
               stderr=subprocess.PIPE, **kwargs):
    """ Run a command using asyncio.

    :param list cmd: List containing the command to run, plus any args.
    :param dict **kwargs:
    """
    env = dict(app.env, **(env or {}))

    proc = await asyncio.create_subprocess_exec(*cmd,
                                                stdin=stdin,
                                                stdout=stdout,
                                                stderr=stderr,
                                                env=env,
                                                **kwargs)

    if isinstance(input, str):
        input = input.encode(encoding)

    stdout_data, stderr_data = await proc.communicate(input)

    if stdout_data is not None:
        stdout_data = stdout_data.decode(encoding)
    if stderr_data is not None:
        stderr_data = stderr_data.decode(encoding)

    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode,
                                            cmd,
                                            stdout_data, stderr_data)
    return (proc.returncode, stdout_data, stderr_data)


async def run_step(step, msg_cb, event_name=None):
    # Define STEP_NAME for use in determining where to store
    # our step results,
    #  redis-cli set "conjure-up.$SPELL_NAME.$STEP_NAME.result" "val"
    app.env['CONJURE_UP_STEP'] = step.name

    step_path = Path(app.config['spell-dir']) / 'steps' / step.filename

    if not step_path.is_file():
        return

    step_path = str(step_path)

    msg = "Running step: {}.".format(step.name)
    app.log.info(msg)
    msg_cb(msg)
    if event_name is not None:
        track_event(event_name, "Started", "")

    if not os.access(step_path, os.X_OK):
        raise Exception("Step {} not executable".format(step.title))

    if is_linux() and step.needs_sudo and not await can_sudo():
        raise SudoError('Step "{}" requires sudo: {}'.format(
            step.title,
            'password failed' if app.sudo_pass else
            'passwordless sudo required',
        ))

    app.log.debug("Executing script: {}".format(step_path))

    async with aiofiles.open(step_path + ".out", 'w') as outf:
        async with aiofiles.open(step_path + ".err", 'w') as errf:
            proc = await asyncio.create_subprocess_exec(step_path,
                                                        env=app.env,
                                                        stdout=outf,
                                                        stderr=errf)
            async with aiofiles.open(step_path + '.out', 'r') as f:
                while proc.returncode is None:
                    async for line in f:
                        msg_cb(line)
                    await asyncio.sleep(0.01)

    out_log = Path(step_path + '.out').read_text()
    err_log = Path(step_path + '.err').read_text()

    if proc.returncode != 0:
        app.sentry.context.merge({'extra': {
            'out_log_tail': out_log[-400:],
            'err_log_tail': err_log[-400:],
        }})
        raise Exception("Failure in step {}".format(step.filename))

    # special case for 00_deploy-done to report masked
    # charm hook failures that were retried automatically
    if not app.noreport:
        failed_apps = set()  # only report each charm once
        for line in err_log.splitlines():
            if 'hook failure, will retry' in line:
                log_leader = line.split()[0]
                unit_name = log_leader.split(':')[-1]
                app_name = unit_name.split('/')[0]
                failed_apps.add(app_name)
        for app_name in failed_apps:
            # report each individually so that Sentry will give us a
            # breakdown of failures per-charm in addition to per-spell
            sentry_report('Retried hook failure', tags={
                'app_name': app_name,
            })

    if event_name is not None:
        track_event(event_name, "Done", "")

    result_key = "conjure-up.{}.{}.result".format(app.config['spell'],
                                                  step.name)
    result = app.state.get(result_key)
    return (result or b'').decode('utf8')


def sentry_report(message=None, exc_info=None, tags=None, **kwargs):
    app.loop.run_in_executor(None, partial(_sentry_report,
                                           message, exc_info, tags, **kwargs))


def _sentry_report(message=None, exc_info=None, tags=None, **kwargs):
    if app.noreport:
        return

    try:
        default_tags = {
            'spell': app.config.get('spell'),
            'cloud_type': app.provider.cloud_type,
            'region': app.provider.region,
            'jaas': app.is_jaas,
            'headless': app.headless,
            'juju_version': juju_version(),
            'lxd_version': lxd_version(),
        }

        if message is not None and exc_info is None:
            event_type = 'raven.events.Message'
            kwargs['message'] = message
            if 'level' not in kwargs:
                kwargs['level'] = logging.WARNING
        else:
            event_type = 'raven.events.Exception'
            if exc_info is None or exc_info is True:
                kwargs['exc_info'] = sys.exc_info()
            else:
                kwargs['exc_info'] = exc_info
            if 'level' not in kwargs:
                kwargs['level'] = logging.ERROR

        kwargs['tags'] = dict(default_tags, **(tags or {}))

        app.sentry.capture(event_type, **kwargs)
    except Exception:
        app.log.exception('Error reporting error')


async def can_sudo(password=None):
    if not password and app.sudo_pass:
        password = app.sudo_pass
    if password:
        opt = '-S'  # stdin
        password = '{}\n'.format(password).encode('utf8')
    else:
        opt = '-n'  # non-interactive
    proc = await asyncio.create_subprocess_exec('sudo', opt, '/bin/true',
                                                stdin=subprocess.PIPE,
                                                stdout=subprocess.DEVNULL,
                                                stderr=subprocess.DEVNULL)
    if password:
        await proc.communicate(password)
    else:
        await proc.wait()
    return proc.returncode == 0


def lxd_version():
    """ Get current LXD version
    """
    if is_darwin():
        return "N/A"

    cmd = run_script('conjure-up.lxd --version')
    if cmd.returncode == 0:
        return parse_version(cmd.stdout.decode().strip())
    else:
        raise Exception("Could not determine LXD version.")


def juju_version():
    """ Get current Juju version
    """
    cmd = run_script('juju version')
    if cmd.returncode == 0:
        return parse_version(cmd.stdout.decode().strip())
    else:
        raise Exception("Could not determine Juju version.")


def snap_version():
    """ Get snap version
    """
    cmd = run_script('snap version')
    if cmd.returncode == 0:
        name_version_str = cmd.stdout.decode().splitlines()[0]
        try:
            name, version = name_version_str.split()
            if '~' in version:
                version, series = version.split('~')
            return parse_version(version)
        except:
            raise Exception("Could not determine Snap version.")


def send_msg(msg, label, color, attrs=['bold']):
    if app.argv.debug:
        print("[{}] {}".format(label, msg))
    elif sys.__stdin__.isatty():
        cprint("[{}] ".format(label),
               color,
               attrs=attrs,
               end="{}\n".format(msg))
    else:
        print("[{}] {}".format(label, msg))


def info(msg):
    send_msg(msg, 'info', 'green')


def error(msg):
    send_msg(msg, 'error', 'red')


def warning(msg):
    send_msg(msg, 'warning', 'yellow')


def install_home():
    """ returns installer user home
    """
    return os.path.expanduser("~" + install_user())


def juju_path():
    """ returns juju path for $user
    """
    return os.getenv('JUJU_DATA',
                     os.path.expanduser('~/.local/share/juju'))


def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)
        chown(path, install_user(), recursive=True)


def merge_dicts(*dicts):
    """
    Return a new dictionary that is the result of merging the arguments
    together.
    In case of conflicts, later arguments take precedence over earlier
    arguments.
    ref:  http://stackoverflow.com/a/8795331/3170835
    """
    updated = {}
    # grab all keys
    keys = set()
    for d in dicts:
        keys = keys.union(set(d))

    for key in keys:
        values = [d[key] for d in dicts if key in d]
        # which ones are mapping types? (aka dict)
        maps = [value for value in values if isinstance(value, Mapping)]
        if maps:
            # if we have any mapping types, call recursively to merge them
            updated[key] = merge_dicts(*maps)
        else:
            # otherwise, just grab the last value we have, since later
            # arguments take precedence over earlier arguments
            updated[key] = values[-1]
    return updated


def chown(path, user, group=None, recursive=False):
    """ Change user/group ownership of file

    Arguments:
    path: path of file or directory
    user: new owner username
    group: new owner group name
    recursive: set files/dirs recursively
    """
    if group is None:
        group = user

    try:
        if not recursive or os.path.isfile(path):
            shutil.chown(path, user, group)
        else:
            for root, dirs, files in os.walk(path):
                shutil.chown(root, user, group)
                for item in dirs:
                    shutil.chown(os.path.join(root, item), user, group)
                for item in files:
                    shutil.chown(os.path.join(root, item), user, group)
    except OSError as e:
        raise e


def spew(path, data, owner=None):
    """ Writes data to path
    Arguments:
    path: path of file to write to
    data: contents to write
    owner: optional owner of file
    """
    with open(path, 'w') as f:
        f.write(data)
    if owner:
        try:
            chown(path, owner)
        except:
            raise Exception(
                "Unable to set ownership of {}".format(path))


def slurp(path):
    """ Reads data from path

    Arguments:
    path: path of file
    """
    try:
        with path.open() as f:
            return f.read().strip()
    except IOError:
        raise IOError


def install_user():
    """ returns current user
    """
    user = os.getenv('USER', None)
    if user is None:
        raise Exception("Unable to determine current user.")
    return user


def setup_metadata_controller():
    """ Pulls in a local bundle or via charmstore api and sets up our
    controller. You can also further customize the bundle by providing a local
    bundle-custom.yaml that will be deep merged over whatever bundle is
    referenced. """
    spell_dir = Path(app.config['spell-dir'])
    bundle_filename = spell_dir / 'bundle.yaml'
    bundle_custom_filename = spell_dir / 'bundle-custom.yaml'

    if bundle_filename.exists():
        # Load bundle data early so we can merge any additional charm options
        bundle_data = yaml.load(bundle_filename.read_text())
    else:
        bundle_name = app.config['metadata'].get('bundle-name', None)
        if bundle_name is None:
            raise Exception(
                "Could not determine a bundle to download, please make sure "
                "the spell contains a 'bundle-name' field."
            )
        bundle_channel = app.argv.channel

        app.log.debug("Pulling bundle for {} from channel: {}".format(
            bundle_name, bundle_channel))
        bundle_data = charm.get_bundle(bundle_name, bundle_channel)

    if bundle_custom_filename.exists():
        bundle_custom = yaml.load(slurp(bundle_custom_filename))
        bundle_data = merge_dicts(bundle_data,
                                  bundle_custom)

    bundle = Bundle(bundle_data=bundle_data)
    app.metadata_controller = MetadataController(bundle, Config('bundle-cfg'))


def set_chosen_spell(spell_name, spell_dir):
    track_event("Spell Choice", spell_name, "")
    app.env['CONJURE_UP_SPELL'] = spell_name
    app.config.update({'spell-dir': spell_dir,
                       'spell': spell_name})


def set_spell_metadata():
    metadata_path = os.path.join(app.config['spell-dir'],
                                 'metadata.yaml')

    with open(metadata_path) as fp:
        metadata = yaml.safe_load(fp.read())

    app.config['metadata'] = metadata


def get_spell_metadata(spell):
    """ Returns metadata about spell
    """
    metadata_path = os.path.join(app.config['spells-dir'],
                                 spell,
                                 'metadata.yaml')
    with open(metadata_path) as fp:
        metadata = yaml.safe_load(fp.read())

    return metadata


def __available_on_darwin(key):
    """ Returns True if spell is available on macOS
    """
    metadata = get_spell_metadata(key)
    if is_darwin() and 'cloud-whitelist' in metadata \
       and 'localhost' in metadata['cloud-whitelist']:
        return False
    return True


def find_spells():
    """ Find spells, excluding localhost only spells if not linux
    """
    _spells = []
    for category, cat_dict in app.spells_index.items():
        for sd in cat_dict['spells']:
            if not __available_on_darwin(sd['key']):
                continue
            _spells.append((category, sd))
    return _spells


def find_spells_matching(key):
    if key in app.spells_index:
        _spells = []
        for sd in app.spells_index[key]['spells']:
            if not __available_on_darwin(sd['key']):
                continue
            _spells.append((key, sd))
        return _spells

    for category, d in app.spells_index.items():
        for spell in d['spells']:
            if spell['key'] == key:
                if not __available_on_darwin(spell['key']):
                    continue
                return [(category, spell)]
    return []


def get_options_whitelist(service_name):
    """returns list of whitelisted option names.
    If there is no whitelist, returns []
    """
    metadata = app.config.get('metadata', None)
    if metadata is None:
        return []

    options_whitelist = metadata.get('options-whitelist', None)
    if options_whitelist is None:
        return []

    svc_opts_whitelist = options_whitelist.get(service_name, [])

    return svc_opts_whitelist


def gen_hash():
    """ generates a UUID
    """
    return str(uuid.uuid4()).split('-')[0][:3]


def gen_model():
    """ generates a unique model name
    """
    name = "conjure-{}".format(app.env['CONJURE_UP_SPELL'])
    return "{}-{}".format(name[:24], gen_hash())


def gen_cloud():
    """ generates a unique cloud
    """
    name = "cloud-{}".format(app.provider.cloud_type)
    return "{}-{}".format(name[:24], gen_hash())


def is_darwin():
    """ Checks if host platform is macOS
    """
    return sys.platform.startswith('darwin')


def is_linux():
    """ Checks if host platform is linux
    """
    return sys.platform.startswith('linux')


def is_valid_hostname(hostname):
    """ Checks if a hostname is valid
    Graciously taken from http://stackoverflow.com/a/2532344/3170835
    """
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    allowed = re.compile("(?!-)[A-Z\d\-\_]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def set_terminal_title(title):
    """ Sets the terminal title
    """
    sys.stdout.write("\x1b]2;{}\x07".format(title))


def get_physical_network_interfaces():
    """ Returns a list of physical network interfaces

    We whitelist eth due to some instances where users run
    conjure-up inside a single LXD container. At that point
    all devices are considered virtual and all network device
    naming follows the ethX pattern.
    """
    sys_class_net = Path('/sys/class/net')
    devices = []
    for device in sys_class_net.glob("*"):
        parts = str(device.resolve()).split('/')
        if "virtual" in parts and not parts[-1].startswith('eth'):
            continue
        try:
            if not get_physical_network_ipaddr(device.name):
                continue
        except Exception:
            continue
        devices.append(device.name)
    if len(devices) == 0:
        raise Exception(
            "Could not find a suitable physical network interface "
            "to create a LXD bridge on. Please check your network "
            "configuration.")
    return sorted(devices)


def get_physical_network_ipaddr(iface):
    """ Gets an IP Address for network device, ipv4 only

    Arguments:
    iface: interface to query
    """
    out = run_script('ip addr show {}'.format(iface))
    if out.returncode != 0:
        raise Exception(
            "Could not determine an IPv4 address for {}".format(iface))

    app.log.debug("Parsing {} for IPv4 address".format(
        out.stdout.decode('utf8')))

    try:
        ipv4_addr = out.stdout.decode(
            'utf8').split('inet ')[1].split('/')[0]
    except IndexError:
        return None
    return ipv4_addr


def get_open_port():
    """ Gets an unused port
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


class IterQueue(asyncio.Queue):
    """
    Queue subclass that supports the ``async for`` syntax.

    When the producer is done adding items, it must call `close` to
    notify the consumer.

    Example::

        queue = IterQueue()

        async def consumer():
            async for line in queue:
                print(line)

        async def producer():
            with open('filename') as fp:
                for line in fp:
                    await queue.put(line)
            queue.close()
    """

    def __init__(self, *args, **kwargs):
        self.sentinal = []
        super().__init__(*args, **kwargs)

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self.get()
        if item is self.sentinal:
            raise StopAsyncIteration
        return item

    async def close(self):
        await self.put(self.sentinal)


class SanitizeDataProcessor(SanitizePasswordsProcessor):
    """
    Sanitize data sent to Sentry.

    Performs the same santiziations as the SanitizePasswordsProcessor, but
    also sanitizes values.
    """

    def sanitize(self, key, value):
        value = super().sanitize(key, value)

        if value is None:
            return value

        def _check_str(s):
            sl = s.lower()
            for field in self.FIELDS:
                if field not in sl:
                    continue
                if 'invalid' in s or 'error' in s:
                    return '***(contains invalid {})***'.format(field)
                else:
                    return '***(contains {})***'.format(field)
            return s

        if isinstance(value, str):
            # handle basic strings
            value = _check_str(value)
        elif isinstance(value, bytes):
            # handle bytes
            value = _check_str(value.decode('utf8', 'replace'))
        elif isinstance(value, (list, tuple, set)):
            # handle list-like
            orig_type = type(value)
            value = list(value)
            for i, item in enumerate(value):
                value[i] = self.sanitize(key, item)
            value = orig_type(value)
        elif isinstance(value, dict):
            # handle dicts
            for key, value in value.items():
                value[key] = self.sanitize(key, value)
        else:
            # handle everything else by sanitizing its JSON encoding
            # note that we don't want to use the JSON encoded value if it's
            # not being santizied, because it will end up double-encoded
            value_json = json.dumps(value)
            sanitized = _check_str(value_json)
            if sanitized != value_json:
                value = sanitized

        return value


class TestError(Exception):
    def __init__(self):
        super().__init__('This is a dummy error for testing reporting')


class SudoError(Exception):
    pass
