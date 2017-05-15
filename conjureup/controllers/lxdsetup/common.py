import os
from pathlib import Path
from subprocess import DEVNULL, CalledProcessError

from conjureup import controllers, utils
from conjureup.app_config import app


class BaseLXDSetupController:
    def __init__(self):
        snap_user_data = os.environ.get('SNAP_USER_DATA', None)
        if snap_user_data:
            self.flag_file = Path(snap_user_data) / 'lxd.setup'
        else:
            self.flag_file = Path(app.env['CONJURE_UP_CACHEDIR']) / 'lxd.setup'
        self.ifaces = utils.get_physical_network_interfaces()

    @property
    def is_ready(self):
        return self.flag_file.exists()

    def next_screen(self):
        return controllers.use('bootstrap').render()

    def setup(self, iface):
        if not isinstance(iface, str):
            iface = iface.network_interface.value
        self.lxd_init(iface)
        self.flag_file.touch()

    def lxd_init(self, iface):
        """ Runs initial lxd init

        Arguments:
        iface: interface name
        """
        lxd_init_cmds = [
            "lxc version",
            "lxd init --auto",
            'lxc config set core.https_address [::]:12001',
            'lxc profile device add default {iface}'
            ' nic nictype=bridged'
            ' parent=conjureup1 name={iface}'.format(iface=iface)
        ]
        for cmd in lxd_init_cmds:
            app.log.debug("LXD Init: {}".format(cmd))
            out = utils.run_script(cmd)
            if out.returncode != 0:
                raise Exception(
                    "Problem running: {}:{}".format(
                        cmd,
                        out.stderr.decode('utf8')))

        self.setup_bridge_network(iface)
        self.setup_unused_bridge_network()

    def setup_bridge_network(self, iface):
        """ Sets up our main network bridge to be used with Localhost deployments
        """
        try:
            utils.run('lxc network show conjureup1', shell=True, check=True,
                      stdout=DEVNULL, stderr=DEVNULL)
        except CalledProcessError:
            out = utils.run_script('lxc network create conjureup1 '
                                   'ipv4.address=10.100.0.1/24 '
                                   'ipv4.nat=true '
                                   'ipv6.address=none '
                                   'ipv6.nat=false')
            if out.returncode != 0:
                raise Exception(
                    "Failed to create LXD network bridge: {}".format(
                        out.stderr.decode()))

            out = utils.run_script(
                'lxc network attach-profile conjureup1 '
                'default {iface} {iface}'.format(
                    iface=iface))
            if out.returncode != 0:
                raise Exception(
                    "Failed to attach LXD network profile: {}".format(
                        out.stderr.decode()))

    def setup_unused_bridge_network(self):
        """ Sets up an unused bridge that can be used with deployments such as
        OpenStack on LXD using NovaLXD.
        """
        out = utils.run_script('lxc network show conjureup0',
                               stdout=DEVNULL,
                               stderr=DEVNULL)
        if out.returncode != 0:
            out = utils.run_script('lxc network create conjureup0 '
                                   'ipv4.address=10.99.0.1/24 '
                                   'ipv4.nat=true '
                                   'ipv6.address=none '
                                   'ipv6.nat=false')
            if out.returncode != 0:
                raise Exception("Failed to create LXD conjureup0 network "
                                "bridge: {}".format(out.stderr.decode('utf8')))
