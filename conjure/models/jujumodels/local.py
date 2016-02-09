from conjure.models.jujumodels.base import JujuModel
from collections import OrderedDict


class LocalJujuModel(JujuModel):
    name = "Local"
    description = "Deploy using containers."
    provider_type = "lxd"
    config = OrderedDict([
        ('apt-http-proxy', None),
        ('apt-https-proxy', None),
        ('http-proxy', None),
        ('https-proxy', None),
        ('enable-os-refresh-update', False),
        ('enable-os-upgrade', False)
    ])
