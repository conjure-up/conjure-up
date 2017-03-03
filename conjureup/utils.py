import codecs
import errno
import os
import pty
import shutil
import sys
import uuid
from collections import Mapping
from subprocess import (
    DEVNULL,
    PIPE,
    CalledProcessError,
    Popen,
    check_call,
    check_output
)

import yaml
from termcolor import cprint

from bundleplacer.bundle import Bundle
from bundleplacer.charmstore_api import MetadataController
from bundleplacer.config import Config
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


def lxd_version():
    """ Get current LXD version
    """
    cmd = run_script('lxc version')
    if cmd.returncode == 0:
        return cmd.stdout.decode().strip()
    else:
        raise Exception("Could not determine LXD version.")


def juju_version():
    """ Get current Juju version
    """
    cmd = run_script('juju version')
    if cmd.returncode == 0:
        return cmd.stdout.decode().strip()
    else:
        raise Exception("Could not determine LXD version.")


def lxd_has_ipv6():
    """ Checks whether LXD bridge has IPv6 enabled
    """
    if check_bridge_exists():
        cmd = run_script('lxc network get lxdbr0 ipv6.nat')
        out = cmd.stdout.decode().strip()
        if "true" in out:
            return True
    return False


def check_bridge_exists():
    """ Checks that an LXD network bridge exists
    """
    try:
        run('lxc network list|grep -q bridge',
            shell=True, check=True)
    except CalledProcessError:
        return False
    return True


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
        with open(path) as f:
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


def load_global_conf():
    """ loads global configuration

    Returns:
    dictionary of config items
    """
    global_conf_file = '/etc/conjure-up.conf'
    if not os.path.exists(global_conf_file):
        global_conf_file = os.path.join(
            os.path.dirname(__file__), '..', 'etc', 'conjure-up.conf')
    try:
        with open(global_conf_file) as fp:
            return yaml.safe_load(fp.read())
    except:
        return {}


def setup_metadata_controller():
    bundle_filename = os.path.join(app.config['spell-dir'], 'bundle.yaml')
    if not os.path.isfile(bundle_filename):
        if 'bundle-location' not in app.config['metadata']:
            raise Exception(
                "Could not determine bundle location: no local bundle "
                "was found and bundle-location not set in spell metadata.")
        bundle_filename = charm.get_bundle(
            app.config['metadata']['bundle-location'], True)

    # Load bundle data early so we can merge any additional charm options
    with open(bundle_filename) as f:
        bundle_data = yaml.load(f)

    bundle_custom_filename = os.path.join(app.config['spell-dir'],
                                          'bundle-custom.yaml')
    if os.path.isfile(bundle_custom_filename):
        with open(bundle_custom_filename) as f:
            bundle_custom = yaml.load(f)
        bundle_data = merge_dicts(bundle_data,
                                  bundle_custom)

    bundle = Bundle(bundle_data=bundle_data)
    bundleplacer_cfg = Config(
        'bundle-placer',
        {
            'bundle_filename': bundle_filename,
            'bundle_key': None,
        })

    app.metadata_controller = MetadataController(bundle, bundleplacer_cfg)


def set_chosen_spell(spell_name, spell_dir):
    track_event("Spell Choice", spell_name, "")
    app.env = os.environ.copy()
    app.env['CONJURE_UP_SPELL'] = spell_name
    app.config.update({'spell-dir': spell_dir,
                       'spell': spell_name})


def set_spell_metadata():
    metadata_path = os.path.join(app.config['spell-dir'],
                                 'metadata.yaml')

    with open(metadata_path) as fp:
        metadata = yaml.safe_load(fp.read())

    app.config['metadata'] = metadata


def find_spells_matching(key):
    if key in app.spells_index:
        return [(key, sd) for sd in app.spells_index[key]['spells']]

    for category, d in app.spells_index.items():
        for spell in d['spells']:
            if spell['key'] == key:
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
