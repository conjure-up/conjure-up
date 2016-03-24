import shutil
import os
from subprocess import check_call, CalledProcessError
from conjure.models.bundle import BundleModel
from conjure.async import submit


class UtilsException(Exception):
    """ Error in utils
    """
    pass


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
        raise UtilsException(e)


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
            raise UtilsException(
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
    user = os.getenv('SUDO_USER', None)
    if not user:
        user = os.getenv('USER', 'root')
    return user


def pollinate(session, tag, log):
    """ fetches random seed

    Tag definitions:
        WS - welcome shown
        BS - bundle selected
        CS - cloud selected
        CC - cloud creation started
        CA - cloud credentials added
        JS - juju bootstrap started
        JC - juju bootstrap completed
        CS - controller selected
        PM - placement/bundle editor shown (maas)
        PS - placement/bundle editor shown (other)
        PC - placements committed
        SS - deploy summary shown
        DS - deploy started
        DC - deploy complete (currently unused)

        UC - user cancelled
        EC - error getting credentials
        EP - error in placement/bundle editor
        EB - error juju bootstrap
        ED - error deploying (unused)

    Arguments:
    session: randomly generated session id
    tag: custom tag
    log: logger
    """
    if not os.path.isfile('/usr/bin/pollinate'):
        log.warning("pollinate binary not found")
        return
    bundle_key = BundleModel.key()
    if not bundle_key:
        bundle_key = '-'
    agent_str = 'conjure/{}/{}/{}'.format(session, bundle_key, tag)
    def do_pollinate():
        try:
            cmd = ("sudo su - -c 'pollinate -q -r --curl-opts "
                   "\"-k --user-agent {}\"'".format(agent_str))
            log.info("pollinate: {}".format(cmd))
            check_call(cmd, shell=True)
        except CalledProcessError as e:
            log.warning("Generating random seed failed: {}".format(e))
    submit(do_pollinate, lambda _: None)
