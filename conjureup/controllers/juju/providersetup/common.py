from conjureup import controllers
from conjureup.app_config import app
from conjureup.consts import cloud_types


class ProviderSetupController:
    def render(self, going_back=False):
        if going_back:
            app.log.info('provider: going back')
            controllers.use('regions').render(going_back=True)
        elif app.provider.cloud_type == cloud_types.LOCAL:
            controllers.use('lxdsetup').render()
        elif app.provider.cloud_type == cloud_types.VSPHERE:
            controllers.use('vspheresetup').render()
        else:
            controllers.use('controllerpicker').render()
