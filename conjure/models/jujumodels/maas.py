from conjure.models.jujumodels.base import JujuModel
from collections import OrderedDict


class MaasJujuModel(JujuModel):
    name = "MAAS"
    description = "Deploy to a MAAS environment."
    provider_type = "maas"
    config = OrderedDict([
        ('maas-server', None),
        ('maas-oauth', None),
        ('enable-os-upgrade', False),
        ('enable-os-refresh-update', False),
    ])
    supports_placement = True
