from conjureup import controllers
from conjureup.app_config import app


class BaseLXDSetupController:
    """ Provides configuration for LXD storage and network

    The following redis keys exist to allow spell/addon authors to make use of
    the lxd selections:

    conjure-up.<spell>.lxd-network-name
    - Name of the selected lxc network bridge
    conjure-up.<spell>.lxd-network
    - CIDR of network
    conjure-up.<spell>.lxd-network-gateway
    - gateway address
    conjure-up.<spell>.lxd-network-dhcp-range-start
    - start of dhcp range
    conjure-up.<spell>.lxd-network-dhcp-range-stop
    - stop of dhcp range
    conjure-up.<spell>.lxd-storage-pool
    - Name of the selected lxc storage pool
    """

    def __init__(self):
        self.state_key = "conjure-up.{}".format(app.config['spell'])

    def set_state(self, key, value):
        key = "{}.{}".format(self.state_key, key)
        return app.state.set(key, value)

    def get_state(self, key):
        key = "{}.{}".format(self.state_key, key)
        return app.state.get(key).decode('utf8')

    def next_screen(self):
        return controllers.use('controllerpicker').render()
