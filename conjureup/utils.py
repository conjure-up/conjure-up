import asyncio
import codecs
import errno
import json
import os
import pty
import shutil
import subprocess
import sys
import uuid
from collections import Mapping
from pathlib import Path
from subprocess import (
    DEVNULL,
    PIPE,
    CalledProcessError,
    Popen,
    check_call,
    check_output
)

import yaml
from bundleplacer.bundle import Bundle
from bundleplacer.charmstore_api import MetadataController
from bundleplacer.config import Config
from pkg_resources import parse_version
from termcolor import cprint

from conjureup import charm
from conjureup.app_config import app
from conjureup.telemetry import track_event


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


async def run_step(step_file, step_title, msg_cb, event_name=None):
    step_path = Path(app.config['spell-dir']) / 'steps' / step_file

    if not step_path.is_file():
        return

    step_path = str(step_path)

    msg = "Running {}.".format(step_title)
    app.log.info(msg)
    msg_cb(msg)
    if event_name is not None:
        track_event(event_name, "Started", "")

    if not os.access(step_path, os.X_OK):
        raise Exception("Step {} not executable".format(step_title))

    while True:
        app.log.debug("Executing script: {}".format(step_path))
        app.log.debug("Env: {}".format(app.env.keys()))

        with open(step_path + ".out", 'w') as outf:
            with open(step_path + ".err", 'w') as errf:
                proc = await asyncio.create_subprocess_exec(step_path,
                                                            env=app.env,
                                                            stdout=outf,
                                                            stderr=errf)
                await proc.wait()
        try:
            stderr = Path(step_path + '.err').read_text()
        except Exception:
            stderr = None

        if proc.returncode != 0:
            raise Exception("Failure in step {}: {}".format(step_file, stderr))

        try:
            result = json.loads(Path(step_path + '.out').read_text())
        except OSError as e:
            raise Exception("Unable to read output from step {}: {}".format(
                step_file, e))
        except json.decoder.JSONDecodeError as e:
            raise Exception("Unable to parse output from step {}: {}".format(
                step_file, e))

        if 'returnCode' not in result:
            raise Exception("Invalid message from step {}".format(step_file))

        if result['returnCode'] != 0:
            raise Exception("Failure in step {}: {}".format(step_file,
                                                            result['message']))

        if result.get('isComplete', True):
            break
        msg_cb("{}, please wait".format(result['message']))

    msg = "Finished {}: {}".format(step_title, result)
    app.log.info(msg)
    msg_cb(msg)
    if event_name is not None:
        track_event(event_name, "Done", "")

    return result['message']


def can_sudo(self, password=None):
    if password:
        password = '{}\n'.format(password).encode('utf8')
        result = subprocess.run(['sudo', '-S', '/bin/true'],
                                input=password,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        if result.returncode != 0:
            return False
    result = subprocess.run(['sudo', '-n', '/bin/true'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    return result.returncode == 0


def lxd_version():
    """ Get current LXD version
    """
    if is_darwin():
        return "N/A"

    cmd = run_script('lxd --version')
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


def lxd_has_ipv6():
    """ Checks whether LXD bridge has IPv6 enabled
    """
    cmd = run_script('lxc network get lxdbr0 ipv6.nat')
    out = cmd.stdout.decode().strip()
    if "true" in out:
        return True
    return False


def check_user_in_group(group):
    """ Checks if a user is associated with `group`
    """
    groups = run_script('groups').stdout.decode()
    if group in groups.split():
        return True
    return False


def check_deb_installed(pkg):
    """ Checks if a debian package is installed
    """
    try:
        run('dpkg-query -W {}'.format(pkg),
            shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
    except CalledProcessError:
        return False
    return True


def send_msg(msg, label, color, attrs=['bold']):
    if sys.__stdin__.isatty():
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


def is_darwin():
    """ Checks if host platform is macOS
    """
    return sys.platform.startswith('darwin')


def is_linux():
    """ Checks if host platform is linux
    """
    return sys.platform.startswith('linux')


def set_terminal_title(title):
    """ Sets the terminal title
    """
    sys.stdout.write("\x1b]2;{}\x07".format(title))


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
