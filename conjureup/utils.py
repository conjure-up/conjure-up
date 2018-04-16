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
from itertools import chain
from pathlib import Path
from subprocess import PIPE, Popen, check_call, check_output

import aiofiles
import yaml
from pkg_resources import parse_version
from raven.processors import SanitizePasswordsProcessor
from termcolor import cprint

from conjureup import charm
from conjureup.app_config import app
from conjureup.bundle import Bundle
from conjureup.models.metadata import SpellMetadata
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
               stdin=PIPE, stdout=PIPE, stderr=PIPE, cb_stdout=None,
               cb_stderr=None, **kwargs):
    """ Run a command using asyncio.

    If ``stdout`` or ``stderr`` are strings, they will treated as filenames
    and the data from the proces will be written (streamed) to them. In this
    case, ``cb_stdout`` and ``cb_stderr`` can be given as callbacks to call
    with each line from the respective handle.

    :param list cmd: List containing the command to run, plus any args.
    :param dict **kwargs:
    """
    env = dict(app.env, **(env or {}))

    outf = None
    errf = None
    try:
        if isinstance(stdout, str):
            outf = await aiofiles.open(stdout, 'w')
            stdout = PIPE
        if isinstance(stderr, str):
            errf = await aiofiles.open(stderr, 'w')
            stderr = PIPE

        proc = await asyncio.create_subprocess_exec(*cmd,
                                                    stdin=stdin,
                                                    stdout=stdout,
                                                    stderr=stderr,
                                                    env=env,
                                                    **kwargs)

        data = {}

        async def tstream(source_name, sink, ui_cb):
            source = getattr(proc, source_name)
            while proc.returncode is None:
                async for line in source:
                    line = line.decode(encoding)
                    if ui_cb:
                        ui_cb(line)
                    data.setdefault(source_name, []).append(line)
                    if sink:
                        await sink.write(line)
                        await sink.flush()
                await asyncio.sleep(0.01)

        tasks = []
        if input:
            if isinstance(input, str):
                input = input.encode(encoding)
                tasks.append(proc._feed_stdin(input))
        if proc.stdout:
            tasks.append(tstream('stdout', outf, cb_stdout))
        if proc.stderr:
            tasks.append(tstream('stderr', errf, cb_stderr))

        await asyncio.gather(*tasks)
        await proc.wait()
    finally:
        if outf:
            await outf.close()
        if errf:
            await errf.close()

    stdout_data = ''.join(data.get('stdout', [])) if proc.stdout else None
    stderr_data = ''.join(data.get('stderr', [])) if proc.stderr else None

    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode,
                                            cmd, stdout_data, stderr_data)
    return (proc.returncode, stdout_data, stderr_data)


def sentry_report(message=None, exc_info=None, tags=None, **kwargs):
    app.loop.run_in_executor(None, partial(_sentry_report,
                                           message, exc_info, tags, **kwargs))


def _sentry_report(message=None, exc_info=None, tags=None, **kwargs):
    if app.no_report:
        return

    try:
        default_tags = {
            'spell': app.config.get('spell'),
            'cloud_type': app.provider.cloud_type if app.provider else None,
            'region': app.provider.region if app.provider else None,
            'jaas': app.is_jaas,
            'headless': app.headless,
            'juju_version': juju_version()
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
        pass


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


def juju_version():
    """ Get current Juju version
    """
    cmd = run_script('{} version'.format(app.juju.bin_path))
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
    if app.conjurefile['color'] == 'auto':
        colorized = sys.__stdout__.isatty()
    elif app.conjurefile['color'] == 'always':
        colorized = True
    else:
        colorized = False

    if app.conjurefile['debug']:
        print("[{}] {}".format(label, msg))
    elif colorized:
        cprint("[{}] ".format(label),
               color,
               attrs=attrs,
               end="{}\n".format(msg), flush=True)
    else:
        print("[{}] {}".format(label, msg), flush=True)


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


def _normalize_bundle(original_bundle, overlay_bundle):
    """ Normalizes top level application/services keys
    """
    if 'applications' in original_bundle and 'services' in overlay_bundle:
        overlay_bundle['applications'] = overlay_bundle.pop('services')

    if 'services' in original_bundle and 'applications' in overlay_bundle:
        overlay_bundle['services'] = overlay_bundle.pop('applications')


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
        lists = [value for value in values if isinstance(value, (list, tuple))]
        if maps:
            # if we have any mapping types, call recursively to merge them
            updated[key] = merge_dicts(*maps)
        elif lists:
            # if any values are lists, we want to merge them (non-recursively)
            # first, ensure all values are lists
            for i in range(len(values)):
                if not isinstance(values[i], (list, tuple)):
                    values[i] = [values[i]]
            # then, merge all of the lists into a single list
            updated[key] = list(chain.from_iterable(values))
        else:
            # otherwise, just grab the last value we have, since later
            # arguments take precedence over earlier arguments
            updated[key] = values[-1]
    return updated


def subtract_dicts(*dicts):
    """
    Return a new dictionary that is the result of subtracting each dict
    from the previous.  Except for mappings, the values of the subsequent
    are ignored and simply all matching keys are removed.  If the value is
    a mapping, however, then only the keys from the sub-mapping are removed,
    recursively.
    """
    result = merge_dicts(dicts[0], {})  # make a deep copy
    for d in dicts[1:]:
        for key, value in d.items():
            if key not in result:
                continue
            if isinstance(value, Mapping):
                result[key] = subtract_dicts(result[key], value)
                if not result[key]:
                    # we removed everything from the mapping,
                    # so remove the whole thing
                    del result[key]
            elif isinstance(value, (list, tuple)):
                if not isinstance(result[key], (list, tuple)):
                    # if the original value isn't a list, then remove it
                    # if it matches any of the values in the given list
                    if result[key] in value:
                        del result[key]
                else:
                    # for lists, remove any matching items (non-recursively)
                    result[key] = [item
                                   for item in result[key]
                                   if item not in value]
                    if not result[key]:
                        # we removed everything from the list,
                        # so remove the whole thing
                        del result[key]
            else:
                del result[key]
    return result


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
        bundle_data = Bundle(yaml.load(bundle_filename.read_text()))
    else:
        bundle_name = app.metadata.bundle_name
        if bundle_name is None:
            raise Exception(
                "Could not determine a bundle to download, please make sure "
                "the spell contains a 'bundle-name' field."
            )
        bundle_channel = app.conjurefile['channel']

        app.log.debug("Pulling bundle for {} from channel: {}".format(
            bundle_name, bundle_channel))
        bundle_data = Bundle(charm.get_bundle(bundle_name, bundle_channel))

    if bundle_custom_filename.exists():
        bundle_custom = yaml.load(slurp(bundle_custom_filename))
        bundle_data.apply(bundle_custom)

    for name in app.selected_addons:
        addon = app.addons[name]
        bundle_data.apply(addon.bundle)

    steps = list(chain(app.steps,
                       chain.from_iterable(app.addons[addon].steps
                                           for addon in app.selected_addons)))
    for step in steps:
        if not (step.bundle_add or step.bundle_remove):
            continue
        if step.bundle_remove:
            fragment = yaml.safe_load(step.bundle_remove.read_text())
            bundle_data.subtract(fragment)
        if step.bundle_add:
            fragment = yaml.safe_load(step.bundle_add.read_text())
            bundle_data.apply(fragment)

    if app.conjurefile['bundle-remove']:
        fragment = yaml.safe_load(app.conjurefile['bundle-remove'].read_text())
        bundle_data.subtract(fragment)
    if app.conjurefile['bundle-add']:
        fragment = yaml.safe_load(app.conjurefile['bundle-add'].read_text())
        bundle_data.apply(fragment)

    app.current_bundle = bundle_data


def set_chosen_spell(spell_name, spell_dir):
    track_event("Spell Choice", spell_name, "")
    app.env['CONJURE_UP_SPELL'] = spell_name
    app.config.update({'spell-dir': spell_dir,
                       'spell': spell_name})


def set_spell_metadata():
    app.metadata = SpellMetadata.load(
        Path(app.config['spell-dir']) / 'metadata.yaml')


def get_spell_metadata(spell):
    """ Returns metadata about spell
    """
    metadata_path = Path(app.config['spells-dir']) / spell / 'metadata.yaml'

    return SpellMetadata.load(metadata_path)


def __available_on_darwin(key):
    """ Returns True if spell is available on macOS
    """
    metadata = get_spell_metadata(key)
    if is_darwin() and metadata.cloud_whitelist \
       and 'localhost' in metadata.cloud_whitelist:
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


def find_addons_matching(key):
    if key in app.addons_aliases:
        return app.addons_aliases[key]
    return {}


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
    metadata = app.metadata
    if metadata is None:
        return []

    options_whitelist = metadata.options_whitelist
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


class UtilsHTTPError(Exception):
    pass
