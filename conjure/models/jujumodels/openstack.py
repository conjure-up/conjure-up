from conjure.models.jujumodels.base import JujuModel
from collections import OrderedDict


class OpenStackJujuModel(JujuModel):
    name = "OpenStack"
    description = "Deploy to an OpenStack environment."
    provider_type = "openstack"
    config = OrderedDict([
        ('username', None),
        ('password', None),
        ('auth-mode', None),
        ('auth-url', None),
        ('network', None),
        ('region', None),
        ('tenant-name', None),
        ('use-default-secgroup', True),
        ('use-floating-ip', True)
    ])
