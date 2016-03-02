""" LXD helpers
"""
from conjure.shell import shell
from conjure.utils import FS


class LXD:

    @classmethod
    def has_ubuntu_image(cls):
        """ Checks if ubuntu-trusty image exists for use within Juju
        """
        return 0 == shell(
            'lxc image alias list|grep -q \'ubuntu-trusty\'').code

    @classmethod
    def import_image(cls, series='trusty'):
        """ Import lxd image

        Params:
        series: Ubuntu distro series (defaults: trusty)
        """
        return shell(
            'lxd-images import ubuntu --alias ubuntu-{}'.format(series))

    @classmethod
    def render_lxd_sh(cls, path):
        """ Renders ~/<project-dir>/lxd.sh script
        """
        # TODO: process template args
        lxd_template = FS.slurp("/usr/share/conjure/lxd.sh")
        FS.spew(path, lxd_template)
        shell("chmod +x {}".format(path))
