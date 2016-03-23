import shutil
import os
import logging
from subprocess import check_call, CalledProcessError, DEVNULL
from conjure.models.bundle import BundleModel

log = logging.getLogger('utils')


class UtilsException(Exception):
    """ Error in utils
    """
    pass


class APT:
    @classmethod
    def install(cls, pkgs):
        """ Install apt packages

        Arguments: list of packages
        """
        if not isinstance(pkgs, list):
            pkgs = [pkgs]
        cmd = ("DEBIAN_FRONTEND=noninteractive sudo -E "
               "/usr/bin/apt-get -qyf "
               "-o Dpkg::Options::=--force-confdef "
               "-o Dpkg::Options::=--force-confold "
               "install {0}".format(" ".join(pkgs)))
        try:
            check_call(cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)
        except CalledProcessError as e:
            raise UtilsException("Problem with package install: {0}".format(e))


class Host:
    """ host utilities
    """

    @classmethod
    def install_user(cls):
        """ returns sudo user
        """
        user = os.getenv('SUDO_USER', None)
        if not user:
            user = os.getenv('USER', 'root')
        return user

    @classmethod
    def install_home(cls):
        """ returns installer user home
        """
        return os.path.expanduser("~" + cls.install_user())

    @classmethod
    def juju_path(cls):
        """ returns juju path for $user
        """
        return os.getenv('JUJU_DATA',
                         os.path.expanduser('~/.local/share/juju'))


class FS:
    """ filesystem utility class
    """
    @classmethod
    def mkdir(cls, path):
        if not os.path.isdir(path):
            os.makedirs(path)
            FS.chown(path, Host.install_user(), recursive=True)

    @classmethod
    def chown(cls, path, user, group=None, recursive=False):
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

    @classmethod
    def spew(cls, path, data, owner=None):
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
                cls.chown(path, owner)
            except:
                raise UtilsException(
                    "Unable to set ownership of {}".format(path))

    @classmethod
    def slurp(cls, path):
        """ Reads data from path

        Arguments:
        path: path of file
        """
        try:
            with open(path) as f:
                return f.read().strip()
        except IOError:
            raise IOError


def pollinate(session, tag):
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

    :param str session: randomly generated session id
    :param str tag: custom tag
    """
    if not os.path.isfile('/usr/bin/pollinate'):
        log.warning("pollinate binary not found")
        return
    bundle_key = BundleModel.key()
    if not bundle_key:
        bundle_key = '-'
    agent_str = 'conjure/{}/{}/{}'.format(session, bundle_key, tag)
    try:
        cmd = ("sudo su - -c 'pollinate -q -r --curl-opts "
               "\"-k --user-agent {}\"'".format(agent_str))
        log.info("pollinate: {}".format(cmd))
        check_call(cmd, shell=True)
    except CalledProcessError as e:
        log.warning("Generating random seed failed: {}".format(e))
