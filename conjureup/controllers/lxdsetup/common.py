import os
from pathlib import Path

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
        self.next_screen()

    def lxd_init(self, iface):
        """ Runs initial lxd init

        Arguments:
        iface: interface name
        """
        lxd_init_cmds = [
            "conjure-up.lxc version",
            'conjure-up.lxc config set core.https_address [::]:12001',
            'conjure-up.lxc storage create default dir',
            'conjure-up.lxc profile device add default '
            'root disk path=/ pool=default',
        ]
        for cmd in lxd_init_cmds:
            app.log.debug("LXD Init: {}".format(cmd))
            out = utils.run_script(cmd)
            if out.returncode != 0:
                if 'already exists' not in out.stderr.decode():
                    raise Exception(
                        "Problem running: {}:{}".format(
                            cmd,
                            out.stderr.decode('utf8')))

        self.setup_bridge_network(iface)
        self.setup_unused_bridge_network()

    def setup_bridge_network(self, iface):
        """ Sets up our main network bridge to be used with Localhost deployments
        """
        out = utils.run_script('conjure-up.lxc network show conjureup1')
        if out.returncode == 0:
            return  # already configured

        out = utils.run_script('conjure-up.lxc network create conjureup1 '
                               'ipv4.address=10.100.0.1/24 '
                               'ipv4.nat=true '
                               'ipv6.address=none '
                               'ipv6.nat=false')
        if out.returncode != 0:
            raise Exception("Failed to create LXD conjureup1 network bridge: "
                            "{}".format(out.stderr.decode()))

        out = utils.run_script(
            'conjure-up.lxc network attach-profile conjureup1 '
            'default eth0 eth0')

        if out.returncode != 0:
            # Skip if device already exists
            if 'device already exists' not in out.stderr.decode():
                raise Exception(
                    "Failed to attach LXD conjureup1 network profile: "
                    "{}".format(out.stderr.decode()))

    def setup_unused_bridge_network(self):
        """ Sets up an unused bridge that can be used with deployments such as
        OpenStack on LXD using NovaLXD.
        """
        out = utils.run_script('conjure-up.lxc network show conjureup0')
        if out.returncode == 0:
            return  # already configured

        out = utils.run_script('conjure-up.lxc network create conjureup0 '
                               'ipv4.address=10.99.0.1/24 '
                               'ipv4.nat=true '
                               'ipv6.address=none '
                               'ipv6.nat=false')

        out = utils.run_script(
            'conjure-up.lxc network attach-profile conjureup0 '
            'default eth1 eth1')

        if out.returncode != 0:
            # Skip if device already exists
            if 'device already exists' not in out.stderr.decode():
                raise Exception(
                    "Failed to attach LXD conjureup0 network profile: "
                    "{}".format(out.stderr.decode()))
