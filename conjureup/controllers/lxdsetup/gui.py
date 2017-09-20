import ipaddress

from conjureup import utils
from conjureup.app_config import app
from conjureup.ui.views.lxdsetup import LXDSetupView

from . import common


class LXDSetupControllerError(Exception):
    pass


class LXDSetupController(common.BaseLXDSetupController):
    async def get_lxd_devices(self):
        self.devices = {
            'networks': await app.provider.get_networks(),
            'storage-pools': await app.provider.get_storage_pools()
        }

        self.view = LXDSetupView(self.devices, self.finish)
        self.view.show()

    async def set_lxd_info(self, network, storage_pool):
        self.set_state('lxd-network-name', network['name'])
        phys_iface_addr = utils.get_physical_network_ipaddr(
            network['name'])
        iface = ipaddress.IPv4Interface(phys_iface_addr)
        self.set_state('lxd-network', iface.network)
        self.set_state('lxd-gateway', iface.ip)
        self.set_state('lxd-network-dhcp-range-start',
                       iface.ip + 1)
        # We already know the gateway is x.x.x.1,
        # subtract 3 puts us at x.x.x.254
        self.set_state('lxd-network-dhcp-range-stop',
                       "{}".format(iface.ip - 3))
        self.set_state('lxd-storage-pool', storage_pool['name'])
        app.log.debug('LXD Info set: '
                      '(name: {}) '
                      '(network: {}) '
                      '(gateway: {}) '
                      '(dhcp-range-start: {}) '
                      '(dhcp-range-stop: {})'.format(
                          self.get_state('lxd-network-name'),
                          self.get_state('lxd-network'),
                          self.get_state('lxd-gateway'),
                          self.get_state('lxd-network-dhcp-range-start'),
                          self.get_state('lxd-network-dhcp-range-stop')))

    def finish(self, network, storage):
        app.loop.create_task(self.set_lxd_info(network, storage))
        return self.next_screen()

    def render(self):
        app.loop.create_task(self.get_lxd_devices())


_controller_class = LXDSetupController
