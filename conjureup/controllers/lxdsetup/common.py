import os
import textwrap
import time
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile

from pkg_resources import parse_version

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

    @property
    def is_snap_compatible(self):
        """ Checks if snap version is new enough
        """
        return utils.snap_version() >= parse_version('2.25')

    def next_screen(self):
        return controllers.use('controllerpicker').render()

    def setup(self, iface):
        # Make sure we're using a newer snapd
        if not self.is_snap_compatible:
            raise Exception(
                "You must be on a snapd version of 2.25 or newer. "
                "Please run `sudo apt update && sudo apt dist-upgrade`.\n\n"
                "Once complete, re-run conjure-up.")
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
            self.set_lxd_init_auto,
            self.set_lxc_config,
            self.set_lxd_storage,
            partial(self.setup_bridge_network, iface),
            self.setup_unused_bridge_network,
            self.set_default_profile
        ]

        for cmd in lxd_init_cmds:
            app.log.debug("LXD Init: {}".format(cmd))
            cmd()

    def set_lxd_storage(self):
        """ Runs lxc storage creation
        """
        out = utils.run_script("conjure-up.lxc storage create default dir")
        if out.returncode != 0:
            if 'already exists' not in out.stderr.decode():
                raise Exception(
                    "Problem running lxc storage: {}".format(
                        out.stderr.decode()))

    def set_lxd_init_auto(self, retries=0):
        """ Runs lxd init --auto

        We want to retry and delay here as LXD daemon may
        not be fully awake yet.
        """
        retries = retries
        max_retries = 5
        delay = 2
        out = utils.run_script("conjure-up.lxd init --auto")
        if out.returncode != 0:
            if retries < max_retries:
                retries += 1
                time.sleep(delay)
                self.set_lxd_init_auto(retries)
            raise Exception(
                "Problem running lxd init: {}".format(out.stderr.decode()))

    def set_lxc_config(self, retries=0):
        """ Runs lxc config

        We want to retry and delay here as LXD daemon may
        not be fully awake yet.
        """
        retries = retries
        max_retries = 5
        delay = 2
        out = utils.run_script(
            "conjure-up.lxc config set core.https_address [::]:12001")
        if out.returncode != 0:
            if retries < max_retries:
                retries += 1
                time.sleep(delay)
                self.set_lxc_config(retries)
            raise Exception(
                "Problem running lxc config: {}".format(out.stderr.decode()))

    def set_default_profile(self):
        """ Sets the default profile with the correct parent network bridges
        """
        profile = textwrap.dedent(
            """
            config:
              boot.autostart: "true"
            description: Default LXD profile
            devices:
              eth0:
                name: eth0
                nictype: bridged
                parent: conjureup1
                type: nic
              eth1:
                name: eth1
                nictype: bridged
                parent: conjureup0
                type: nic
              root:
                path: /
                pool: default
                type: disk
            name: default
            """)
        with NamedTemporaryFile(mode='w', encoding='utf-8',
                                delete=False) as tempf:
            utils.spew(tempf.name, profile)
            out = utils.run_script(
                'cat {} |conjure-up.lxc profile edit default'.format(
                    tempf.name))
            if out.returncode != 0:
                raise Exception("Problem setting default profile: {}".format(
                    out))

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

        if out.returncode != 0:
            raise Exception(
                "Failed to create conjureup0 network bridge: "
                "{}".format(out.stderr.decode()))
