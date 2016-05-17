from configobj import ConfigObj
import os


def check_bridge_exists():
    """ Checks that an LXD network bridge exists
    """
    if os.path.isfile('/etc/default/lxd-bridge'):
        cfg = ConfigObj('/etc/default/lxd-bridge')
    else:
        cfg = ConfigObj()

    ready = cfg.get('LXD_IPV4_ADDR', None)
    if not ready:
        return False
    return True
