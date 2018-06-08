import asyncio

from conjureup import controllers
from conjureup.app_config import app
from conjureup.ui.views.interstitial import InterstitialView
from conjureup.ui.views.vspheresetup import VSphereSetupView

from . import common


class VSphereSetupController(common.BaseVSphereSetupController):
    def __init__(self):
        self.authenticating = asyncio.Event()

    def render(self):
        self.render_interstitial()
        app.loop.create_task(self.login_to_vsphere())

    async def login_to_vsphere(self):
        # Assign current datacenter
        await app.provider.login()
        datacenter = None
        for dc in await app.provider.get_datacenters():
            if dc.name == app.provider.region:
                datacenter = dc
        if datacenter is None:
            raise common.VSphereRegionError(
                'Unable to get info for region {}'.format(app.provider.region))
        self.authenticating.clear()
        self.render_setup(datacenter)

    def render_setup(self, datacenter):
        self.view = VSphereSetupView(datacenter,
                                     self.finish,
                                     self.back)
        self.view.show()

    def render_interstitial(self):
        self.authenticating.set()
        view = InterstitialView(title="VSphere Login Wait",
                                message="Logging in to VSphere. Please wait.",
                                event=self.authenticating)
        view.show()

    def back(self):
        controllers.use('providersetup').render(going_back=True)


_controller_class = VSphereSetupController
