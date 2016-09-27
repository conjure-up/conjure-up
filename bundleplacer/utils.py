# Copyright 2014-2016 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import configparser
import errno
import fnmatch
import itertools
import json
import logging
import os
import random
import re
import shutil
import string
import sys
import time
from contextlib import contextmanager
from subprocess import (
    DEVNULL,
    PIPE,
    CalledProcessError,
    Popen,
    call,
    check_call
)
from urllib.parse import urlparse

import requests
import urwid
import yaml
from jinja2 import Environment, FileSystemLoader

try:
    from collections import Mapping
except ImportError:
    Mapping = dict


log = logging.getLogger('bundleplacer')

# String with number of minutes, or None.
blank_len = None


class UtilsException(Exception):
    pass


def cleanup(cfg):
    # Save latest config object
    log.info("Cleanup, saving latest config object.")
    cfg.save()
    pid = os.path.join(install_home(), '.cloud-install/openstack.pid')
    if os.path.isfile(pid):
        os.remove(pid)
    if not cfg.getopt('headless') and cfg.getopt('gui_started'):
        log.debug('Attempting to reset the terminal')
        sys.stderr.write("\x1b[2J\x1b[H")
        call(['stty', 'sane'])
    return


def write_status_file(status='', msg=''):
    """ Writes out a status file

    :param str status: success or fail
    :param str msg: any error/success output
    """
    status_file = os.path.join(install_home(), '.cloud-install/finished.json')
    spew(status_file, json.dumps(dict(status=status, msg=msg)))


def sanitize_cli_opts(opts):
    """ removes false and null items from argument list """
    return {k: v for k, v in vars(opts).items() if v}


def populate_config(opts):
    """ populate configuration suitable for loading in the config
    object merging in cli options.

    :param opts: argparse Namespace class of options
    """
    cfg_from_cli = sanitize_cli_opts(opts)
    if 'config_file' not in opts:
        return cfg_from_cli

    # Override config items from local config
    if opts.config_file:
        cfg_override = yaml.load(slurp(opts.config_file))
        return merge_dicts(cfg_from_cli, cfg_override)


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


def render_charm_config(config):
    """ Render a config for setting charm config options

    If a custom charm config is passed on the cli it will
    attempt to merge those additional settings without losing
    any pre-existing charm options.
    """
    charm_conf = load_template('charmconf.yaml')
    template_args = dict(
        install_type=config.getopt('install_type'),
        openstack_password=config.getopt('openstack_password'))

    os_branch = config.getopt('openstack_git_branch')
    os_release = config.getopt('openstack_release')
    if os_branch:
        if os_branch == 'master':
            template_args['openstack_git_branch'] = os_branch
        else:
            template_args['openstack_git_branch'] = "{}/{}".format(os_branch,
                                                                   os_release)
    template_args['openstack_release'] = os_release

    ubuntu_series = config.getopt('ubuntu_series')
    # Per the charm docs, the openstack charms support
    # openstack-origin: cloud:series-release for a subset of possible
    # combinations - in particular, precise-icehouse and
    # trusty-{juno,kilo,liberty}. If you want to use another series,
    # you don't get to pick the openstack release, you have to use the
    # default, e.g. wily-liberty.
    if ubuntu_series == "trusty":
        openstack_release = config.getopt('openstack_release')
        openstack_origin = ("cloud:{}-{}".format(ubuntu_series,
                                                 openstack_release))
        template_args['openstack_origin'] = openstack_origin

    if config.is_single():
        template_args['worker_multiplier'] = '1'

    # add http proxy settings - should not be necessary as juju sets
    # these in the charm execution environment, but required for
    # openstack-origin-git. See: https://launchpad.net/bugs/1472357

    for pk in ['http_proxy', 'https_proxy']:
        pv = config.getopt(pk)
        if pv:
            template_args[pk] = pv

    charm_conf_modified = charm_conf.render(**template_args)
    dest_yaml_path = os.path.join(config.cfg_path, 'charmconf.yaml')
    spew(dest_yaml_path, charm_conf_modified)

    # Check for custom charm options
    charm_conf_custom_file = config.getopt('charm_config_file')
    if charm_conf_custom_file and os.path.exists(charm_conf_custom_file):
        log.debug("Found custom charm config, updating charm settings.")
        charm_conf = yaml.load(slurp(dest_yaml_path))
        charm_conf_custom = yaml.load(
            slurp(config.getopt('charm_config_file')))
        charm_conf_merged = merge_dicts(charm_conf,
                                        charm_conf_custom)
        spew(dest_yaml_path, yaml.safe_dump(
            charm_conf_merged, default_flow_style=False))


def chown(path, user, group=None, recursive=False):
    """
    Change user/group ownership of file

    :param path: path of file or directory
    :param str user: new owner username
    :param str group: new owner group name
    :param bool recursive: set files/dirs recursively

    """
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
        raise UtilsException(e)


def ensure_locale():
    """
    Makes sure LC_ALL is defined to something sensible
    """
    locale_conf = slurp('/etc/default/locale')
    for line in locale_conf.split('\n'):
        if line.startswith('#'):
            continue
        if "LC_ALL" in line:
            return
    new_locale = "LC_ALL=\"{}\"".format(os.getenv('LANG', 'C'))
    with open('/etc/default/locale', 'a+') as f:
        f.write(new_locale)
    return


def apt_install(pkgs):
    """ runs apt-get install against space separated list of `pkgs`
    """
    ensure_locale()
    cmd = ("DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get -qyf "
           "-o Dpkg::Options::=--force-confdef "
           "-o Dpkg::Options::=--force-confold "
           "install {0}".format(pkgs))
    try:
        check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)
    except CalledProcessError as e:
        log.error("Problem with package install: {0}".format(e))
        pass


def get_command_output(command, timeout=None, user_sudo=False):
    """ Execute command through system shell

    :param command: command to run
    :param timeout: (optional) use 'timeout' to limit time. default 300
    :param user_sudo: (optional) sudo into install users env. default False.
    :type command: str
    :returns: {status: returncode, output: stdout, err: stderr}
    :rtype: dict

    .. code::

        # Get output of juju status
        cmd_dict = utils.get_command_output('juju status')
    """
    cmd_env = os.environ.copy()
    # set consistent locale
    cmd_env['LC_ALL'] = 'C'
    if timeout:
        command = "timeout %ds %s" % (timeout, command)

    if user_sudo:
        command = "sudo -E -H -u {0} {1}".format(install_user(), command)

    try:
        p = Popen(command, shell=True,
                  stdout=PIPE, stderr=PIPE,
                  bufsize=-1, env=cmd_env, close_fds=True)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return dict(ret=127, output="", err="")
        else:
            raise e
    stdout, stderr = p.communicate()
    if p.returncode == 126 or p.returncode == 127:
        stdout = bytes()
    if not stderr:
        stderr = bytes()
    return dict(status=p.returncode,
                output=stdout.decode('utf-8'),
                err=stderr.decode('utf-8'))


def poll_until_true(cmd, predicate, frequency, timeout=600,
                    ignore_exceptions=False):
    """run get_command_output(cmd) every frequency seconds, until
    predicate(output) returns True. Timeout after timeout seconds.

    returns True if call eventually succeeded, or False if timeout was
    reached.

    Exceptions raised during get_command_output are handled as per
    ignore_exceptions. If True, they are just logged. If False, they
    are re-raised.

    """
    start_time = time.time()
    frequency_stub = time.time()
    while True:
        # continue if frequency not met
        if time.time() - frequency_stub <= frequency:
            continue
        try:
            output = get_command_output(cmd)
        except Exception as e:
            if not ignore_exceptions:
                raise e
            else:
                log.debug("**Ignoring** exception: {}".format(e))
        if predicate(output):
            return True
        if time.time() - start_time >= timeout:
            return False


def remote_cp(machine_id, src, dst, juju_home):
    log.debug("Remote copying {src} to {dst} on machine {m}".format(
        src=src,
        dst=dst,
        m=machine_id))
    ret = get_command_output(
        "{juju_home} juju scp {src} {m}:{dst}".format(
            juju_home=juju_home, src=src, dst=dst, m=machine_id))
    log.debug("Remote copy result: {r}".format(r=ret))


def remote_run(machine_id, cmds, juju_home):
    if type(cmds) is list:
        cmds = " && ".join(cmds)
    log.debug("Remote running ({cmds}) on machine {m}".format(
        m=machine_id, cmds=cmds))
    ret = get_command_output(
        "{juju_home} juju run "
        "--machine {m} '{cmds}'".format(juju_home=juju_home,
                                        m=machine_id,
                                        cmds=cmds))
    log.debug("Remote run result: {r}".format(r=ret))
    return ret


def get_host_mem():
    """ Get host memory

    Mostly used as a backup if no data can be pulled from
    the normal means in Machine()
    """
    cmd = get_command_output('head -n1 /proc/meminfo')
    out = cmd['output'].rstrip()
    regex = re.compile('^MemTotal:\s+(\d+)\skB')
    match = re.match(regex, out)
    if match:
        mem = match.group(1)
        mem = int(mem) / 1024 / 1024 + 1
        return int(mem)
    else:
        return 0


def get_host_storage():
    """ Get host storage

    LXC doesn't report storage so we pull from host
    """
    cmd = get_command_output('df -B G --total -l --output=avail'
                             ' -x devtmpfs -x tmpfs | tail -n 1'
                             ' | tr -d "G"')
    if not cmd['status']:
        return cmd['output'].lstrip()
    else:
        return 0


def get_host_cpu_cores():
    """ Get host cpu-cores

    A backup if no data can be pulled from
    Machine()
    """
    cmd = get_command_output('nproc')
    if cmd['output']:
        return cmd['output'].strip()
    else:
        return 'N/A'


def partition(pred, iterable):
    """ Returns tuple of allocated and unallocated systems

    :param pred: status predicate
    :type pred: function
    :param iterable: machine data
    :type iterable: list
    :returns: ([allocated], [unallocated])
    :rtype: tuple

    .. code::

        def is_allocated(d):
            allocated_states = ['started', 'pending', 'down']
            return 'charms' in d or d['agent_state'] in allocated_states
        allocated, unallocated = utils.partition(is_allocated,
                                                 [{state: 'pending'}])
    """
    yes, no = [], []
    for i in iterable:
        (yes if pred(i) else no).append(i)
    return (yes, no)


def reset_blanking():
    global blank_len
    if blank_len is not None:
        call(('setterm', '-blank', blank_len))


@contextmanager
def console_blank():
    global blank_len
    try:
        with open('/sys/module/kernel/parameters/consoleblank') as f:
            blank_len = f.read()
    except (IOError, FileNotFoundError):  # NOQA
        blank_len = None
    else:
        # Cannot use anything that captures stdout, because it is needed
        # by the setterm command to write to the console.
        call(('setterm', '-blank', '0'))
        # Convert the interval from seconds to minutes.
        blank_len = str(int(blank_len) // 60)

    yield

    reset_blanking()


def randomString(size=6, chars=string.ascii_uppercase + string.digits):
    """ Generate a random string

    :param size: number of string characters
    :type size: int
    :param chars: range of characters (optional)
    :type chars: str

    :returns: a random string
    :rtype: str
    """
    return ''.join(random.choice(chars) for x in range(size))


def random_password(size=32):
    """ Generate a password

    :param int size: length of password
    """
    out = get_command_output("pwgen -s {}".format(size))
    return out['output'].strip()


def time_string():
    """ Time helper

    :returns: formatted current time string
    :rtype: str
    """
    return time.strftime('%Y-%m-%d %H:%M')


def find(file_pattern, top_dir, max_depth=None, path_pattern=None):
    """generator function to find files recursively. Usage:

    .. code::

        for filename in find("*.properties", "/var/log/foobar"):
            print filename
    """
    if max_depth:
        base_depth = os.path.dirname(top_dir).count(os.path.sep)
        max_depth += base_depth

    for path, dirlist, filelist in os.walk(top_dir):
        if max_depth and path.count(os.path.sep) >= max_depth:
            del dirlist[:]

        if path_pattern and not fnmatch.fnmatch(path, path_pattern):
            continue

        for name in fnmatch.filter(filelist, file_pattern):
            yield os.path.join(path, name)


def load_template(name, path=None):
    """ load template file

    :param str name: name of template file
    :param str path: alternate location of template location
    """
    if path is None:
        path = '/usr/share/openstack/templates'
    env = Environment(
        loader=FileSystemLoader(path))
    return env.get_template(name)


def install_user():
    """ returns sudo user
    """
    user = os.getenv('SUDO_USER', None)
    if not user:
        user = os.getenv('USER', 'root')
    return user


def install_home():
    """ returns installer user home
    """
    return os.path.expanduser("~" + install_user())


def ssh_readkey():
    """ reads ssh key
    """
    with open(ssh_pubkey(), 'r') as f:
        return f.read()


def ssh_genkey():
    """ Generates sshkey
    """
    if not os.path.exists(ssh_privkey()):
        user_sshkey_path = os.path.join(install_home(),
                                        '.ssh/id_rsa')
        cmd = "ssh-keygen -N '' -f {0}".format(user_sshkey_path)
        out = get_command_output(cmd, user_sudo=True)
        if out['status'] != 0:
            raise Exception(
                "Unable to generate key: {0}".format(out['output']))
        get_command_output('sudo chown -R {0} {1}'.format(
            install_user(),
            os.path.join(install_home(), '.ssh')))
        get_command_output('chmod 0644 {0}.pub'.format(user_sshkey_path),
                           user_sudo=True)
    else:
        log.debug('ssh keys exist for this user, they will be used instead.')


def read_ini(path):
    """ Reads a basic INI like file without sections headers.
    Prepends a default section header for querying.
    """
    ini = open(path)
    config = configparser.ConfigParser()
    config.read_file(itertools.chain(['[DEFAULT]'], ini))
    return config


def ssh_pubkey():
    """ returns path of ssh public key
    """
    return os.path.join(install_home(), '.ssh/id_rsa.pub')


def ssh_privkey():
    """ returns path of private key
    """
    return os.path.join(install_home(), '.ssh/id_rsa')


def spew(path, data, owner=None):
    """ Writes data to path

    :param str path: path of file to write to
    :param str data: contents to write
    :param str owner: optional owner of file
    """
    with open(path, 'w') as f:
        f.write(data)
    if owner:
        try:
            chown(path, owner)
        except:
            raise UtilsException("Unable to set ownership of {}".format(path))


def slurp(path):
    """ Reads data from path

    :param str path: path of file
    """
    try:
        with open(path) as f:
            return f.read().strip()
    except IOError:
        raise IOError


def human_to_mb(s):
    """Translates human-readable strings like '10G' to numeric
    megabytes"""

    if len(s) == 0:
        raise Exception("unexpected empty string")

    md = dict(M=1, G=1024, T=1024 * 1024, P=1024 * 1024 * 1024)
    suffix = s[-1]
    if suffix.isalpha():
        return float(s[:-1]) * md[suffix]
    else:
        return float(s)


def mb_to_human(num):
    """Translates float number of bytes into human readable strings."""
    suffixes = ['M', 'G', 'T', 'P']
    if num == 0:
        return '0 B'

    i = 0
    while num >= 1024 and i < len(suffixes) - 1:
        num /= 1024
        i += 1
    return "{:.2f} {}".format(num, suffixes[i])


def format_constraint(k, v):
    vs = str(v)
    if vs.isdecimal():
        vs = mb_to_human(v)
    return "{}={}".format(k, vs)


def make_screen_hicolor(screen):
    """returns a screen to pass to MainLoop init
    with 256 colors.
    """
    screen.set_terminal_properties(256)
    screen.reset_default_terminal_palette()
    return screen


def get_hicolor_screen(palette):
    screen = urwid.raw_display.Screen()
    screen.register_palette(palette)
    return make_screen_hicolor(screen)


def macgen():
    """ generates mac addresses
    """
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


def download_url(url, output_file):
    """ Downloads contents from a URL
    :param str url: HTTP resource
    :param str output_file: path to store downloaded contents
    """
    res = requests.get(url)
    if res.ok:
        spew(output_file, res.content.decode('utf-8'))
    else:
        raise UtilsException("Exception downloading {}:{}".format(
            url, res.content))


def pollinate(session, tag):
    """ fetches random seed

    :param str session: randomly generated session id
    :param str tag: custom tag
    """
    if not os.path.isfile('/usr/bin/pollinate'):
        return
    if tag not in ['IL', 'IS', 'IM', 'DL', 'DM', 'DS']:
        raise UtilsException("Unknown TAG {}".format(tag))

    session = os.getenv('OSI_TESTRUNNER_ID', session)
    agent_str = 'uoi/{}/{}'.format(session, tag)
    try:
        cmd = ("sudo su - -c 'pollinate -q -r --curl-opts "
               "\"--user-agent {}\"'".format(agent_str))
        log.info("pollinate: {}".format(cmd))
        check_call(cmd, shell=True)
    except CalledProcessError as e:
        log.warning("Generating random seed failed: {}".format(e))


def parse_openstack_creds(creds_file):
    """ Parses openstack-{admin,ubuntu}-rc for openstack
    credentials
    """
    def sanitize_quotes(key):
        if key[0] == key[-1] and key[0] in ("'", '"'):
            return key[1:-1]
        else:
            return key

    cred_map = {}
    rc = slurp(creds_file)
    lines = rc.split("\n")
    for k in lines:
        first, rest = k.split("=")
        first = first.lower()
        if 'username' in first:
            cred_map['username'] = sanitize_quotes(rest)
        if 'password' in first:
            cred_map['password'] = sanitize_quotes(rest)
        if 'tenant_name' in first:
            cred_map['tenant_name'] = sanitize_quotes(rest)
        if 'auth_url' in first:
            cred_map['auth_url'] = urlparse(sanitize_quotes(rest))
        if 'region_name' in first:
            cred_map['region_name'] = sanitize_quotes(rest)
    return cred_map
