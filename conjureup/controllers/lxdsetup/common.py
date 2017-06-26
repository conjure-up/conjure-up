import grp
import os
import textwrap
import time
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile

import psutil
from pkg_resources import parse_version

from conjureup import controllers, utils
from conjureup.app_config import app


class LXDInvalidUserError(Exception):
    """ User is not part of LXD group
    """
    pass


class LXDSnapVersionError(Exception):
    """ Snap version is not compatible
    """
    pass


class BaseLXDSetupController:
    def __init__(self):
        snap_user_data = os.environ.get('SNAP_USER_DATA', None)
        self.lxd_common_dir = Path('/var/snap/conjure-up/common/lxd')
        if snap_user_data:
            self.flag_file = Path(snap_user_data) / 'lxd.setup'
        else:
            self.flag_file = Path(app.env['CONJURE_UP_CACHEDIR']) / 'lxd.setup'
        if self.flag_file.exists():
            # Cleanup from previous runs
            self.flag_file.unlink()
        self.ifaces = utils.get_physical_network_interfaces()

    @property
    def is_snap_compatible(self):
        """ Checks if snap version is new enough
        """
        return utils.snap_version() >= parse_version('2.25')

    def can_user_acces_lxd(self):
        """ Makes sure the user is in the LXD group so they can
        access the daemon
        """
        lxd_group = grp.getgrnam('lxd')
        if os.environ.get('USER', None) not in lxd_group.gr_mem:
            raise LXDInvalidUserError(
                "Your user does not exist in the LXD group, "
                "you can create it with:\n\n"
                " $ sudo usermod -a -G lxd $USER"
                "\n\n"
                "Once complete either log your user out completely, "
                "reboot, or run: \n\n"
                " $ newgrp lxd"
            )

    def next_screen(self):
        return controllers.use('controllerpicker').render()

    def setup(self, iface):
        # Make sure we're using a newer snapd
        if not self.is_snap_compatible:
            raise LXDSnapVersionError(
                "You must be on a snapd version of 2.25 or newer. "
                "Please run `sudo apt update && sudo apt dist-upgrade`.\n\n"
                "Once complete, re-run conjure-up.")
        if not isinstance(iface, str):
            iface = iface.network_interface.value
        self.can_user_acces_lxd()
        self.lxd_init(iface)
        self.next_screen()

    def lxd_init(self, iface):
        """ Runs initial lxd init

        LXD init --auto will return successfully if it's already setup
        otherwise it'll start a new LXD configuration, can be run
        multiple times.

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

    def set_lxd_init_auto(self):
        """ Runs lxd init --auto

        We want to retry and delay here as LXD daemon may
        not be fully awake yet.
        """
        delay = 2
        for attempt in range(5):
            out = utils.run_script("conjure-up.lxd init --auto")
            if out.returncode == 0:
                return
            time.sleep(delay)
        raise Exception(
            "Problem running lxd init: {}".format(out.stderr.decode()))

    def set_lxc_config(self):
        """ Runs lxc config

        Assigns an unused port to our LXD daemon, skips if already set.
        We also want to retry here just incase the daemon isn't ready.
        """
        delay = 2
        for attempt in range(5):
            out = utils.run_script(
                "conjure-up.lxc config get core.https_address"
            )
            if out.stdout.decode().strip():
                return
            out = utils.run_script(
                "conjure-up.lxc config set "
                "core.https_address [::]:{}".format(utils.get_open_port()))
            if out.returncode == 0:
                return
            time.sleep(delay)
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

    def kill_dnsmasq(self, iface):
        """
        If we are going to create a network make sure dnsmasq isn't
        holding onto an interface from a previous install.
        """
        app.log.debug('Attempting to kill dnsmasq for {}'.format(iface))
        for proc in psutil.process_iter():
            if proc.name == 'dnsmasq' and iface in proc.cmdline():
                proc.kill()

        # Not entirely comfortable relying on the pids matching
        # during an upgrade. But remove the pid file if exists.
        dnsmasq_pid_path = self.lxd_common_dir / 'networks' /\
            iface / 'dnsmasq.pid'

        if dnsmasq_pid_path.exists():
            dnsmasq_pid_path.unlink()

    def setup_bridge_network(self, iface):
        """ Sets up our main network bridge to be used with Localhost deployments
        """
        out = utils.run_script('conjure-up.lxc network show conjureup1')
        if out.returncode == 0:
            return  # already configured

        self.kill_dnsmasq('conjureup1')
        out = utils.run_script('conjure-up.lxc network create conjureup1 '
                               'ipv4.address=auto '
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

        self.kill_dnsmasq('conjureup0')
        out = utils.run_script('conjure-up.lxc network create conjureup0 '
                               'ipv4.address=auto '
                               'ipv4.nat=true '
                               'ipv6.address=none '
                               'ipv6.nat=false')

        if out.returncode != 0:
            raise Exception(
                "Failed to create conjureup0 network bridge: "
                "{}".format(out.stderr.decode()))
