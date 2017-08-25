import ipaddress

from conjureup import utils
from conjureup.app_config import app
from conjureup.ui.views.lxdsetup import LXDSetupView

from . import common


class LXDSetupControllerError(Exception):
    pass


class LXDSetupController(common.BaseLXDSetupController):
    async def get_lxd_devices(self):
        devices = {
            'networks': await app.provider.get_networks(),
            'storage-pools': await app.provider.get_storage_pools()
        }

        self.view = LXDSetupView(devices, self.finish)
        self.view.show()

    async def set_lxd_info(self, data):
        if not (data.get('network', None) or data.get('storage-pool', None)):
            raise LXDSetupControllerError(
                "Could not determine a network or storage pool "
                "to continue. Please make sure you have at least "
                "1 network bridge and 1 storage pool: see `lxc network list` "
                "and lxc storage list`. (data: {})".format(data))
        net_info = await app.provider.get_network_info(data['network'])
        self.set_state('lxd-network-name', net_info['name'])
        phys_iface_addr = utils.get_physical_network_ipaddr(
            net_info['name'])
        iface = ipaddress.IPv4Interface(phys_iface_addr)
        self.set_state('lxd-network', iface.network)
        self.set_state('lxd-gateway', iface.ip)
        self.set_state('lxd-network-dhcp-range-start',
                       iface.ip + 1)
        # To account for current interface taking 1 ip
        number_of_hosts = len(list(iface.network.hosts())) - 1
        self.set_state('lxd-network-dhcp-range-stop',
                       "{}".format(iface.ip + number_of_hosts))
        self.set_state('lxd-storage-pool', data['storage-pool'])
        app.log.debug('LXD Info set: (network: {}) '
                      '(gateway: {}) '
                      '(dhcp-range-start: {}) '
                      '(dhcp-range-stop: {})'.format(
                          self.get_state('lxd-network'),
                          self.get_state('lxd-gateway'),
                          self.get_state('lxd-network-dhcp-range-start'),
                          self.get_state('lxd-network-dhcp-range-stop')))

    def finish(self, data):
        app.loop.create_task(self.set_lxd_info(data))
        return self.next_screen()

    def render(self):
        app.loop.create_task(self.get_lxd_devices())


_controller_class = LXDSetupController
