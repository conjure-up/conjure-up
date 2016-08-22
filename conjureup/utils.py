import shutil
import os
import yaml
import pty
import codecs
import errno
from termcolor import colored
from subprocess import (run, check_call,
                        CalledProcessError, DEVNULL,
                        PIPE, Popen)
from conjureup.async import submit
from conjureup import charm
from conjureup.app_config import app
from configobj import ConfigObj

from bundleplacer.bundle import Bundle
from bundleplacer.config import Config
from bundleplacer.charmstore_api import MetadataController


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


def check_bridge_exists():
    """ Checks that an LXD network bridge exists
    """
    if os.path.isfile('/etc/default/lxd-bridge'):
        cfg = ConfigObj('/etc/default/lxd-bridge')
    else:
        cfg = ConfigObj()

    ready = cfg.get('LXD_IPV4_ADDR', None)
    if not ready:
        return False
    return True


def check_deb_installed(pkg):
    """ Checks if a debian package is installed
    """
    try:
        run('dpkg-query -W {}'.format(pkg),
            shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
    except CalledProcessError:
        return False
    return True


def info(msg):
    prefix = colored('[info]', 'green', attrs=['bold'])
    print("{} {}".format(prefix, msg))


def error(msg):
    prefix = colored('[error]', 'red', attrs=['bold'])
    print("{} {}".format(prefix, msg))


def warning(msg):
    prefix = colored('[warning]', 'yellow', attrs=['bold'])
    print("{} {}".format(prefix, msg))


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
    """ returns sudo user
    """
    user = os.getenv('USER', None)
    if user is None:
        raise Exception("Unable to determine current user.")
    return user


def pollinate(session, tag):
    """ fetches random seed

    Tag definitions:
        W001 - welcome shown
        B001 - bundle selected
        CS - cloud selected
        CC - cloud creation started
        CA - cloud credentials added
        L001 - LXD Setup started
        L002 - LXD Setup completed
        J001 - juju post-bootstrap started
        J002 - juju post-bootstrap completed
        J003 - juju bootstrap started
        J004 - juju bootstrap completed
        CS - controller selected
        PM - placement/bundle editor shown (maas)
        PS - placement/bundle editor shown (other)
        PC - placements committed
        SS - deploy summary shown
        DS - deploy started
        DC - deploy complete
        XA - pre processing started
        XB - post processing started

        UC - user cancelled
        EC - error getting credentials
        EP - error in placement/bundle editor
        EB - error juju bootstrap
        ED - error deploying
        E001 - error in post bootstrap phase
        E002 - error in post processor
        E003 - error in pre processor
        E004 - error creating model in existing controller
        E005 - error in picking spells

    Arguments:
    session: randomly generated session id
    tag: custom tag
    """
    agent_str = 'conjure/{}/{}'.format(session, tag)

    def do_pollinate():
        try:
            cmd = ("curl -A {} --connect-timeout 3 --max-time 3 "
                   "--data /dev/null https://entropy.ubuntu.com "
                   "> /dev/null 2>&1".format(
                       agent_str))
            app.log.debug("pollinate: {}".format(cmd))
            check_call(cmd, shell=True)
        except CalledProcessError as e:
            app.log.warning("Generating random seed failed: {}".format(e))
    if not app.argv.debug:
        submit(do_pollinate, lambda _: None)


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

    bundle = Bundle(filename=bundle_filename)
    bundleplacer_cfg = Config(
        'bundle-placer',
        {
            'bundle_filename': bundle_filename,
            'bundle_key': None,
        })

    app.metadata_controller = MetadataController(bundle, bundleplacer_cfg)


def set_chosen_spell(spell_name, spell_dir):
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
        return app.spells_index[key]['spells']

    for k, d in app.spells_index.items():
        for spell in d['spells']:
            if spell['key'] == key:
                return [spell]
    return []
