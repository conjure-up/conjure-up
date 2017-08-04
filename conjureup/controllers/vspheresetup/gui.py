import asyncio

from conjureup.app_config import app
from conjureup.ui.views.bootstrapwait import BootstrapWaitView
from conjureup.ui.views.vspheresetup import VSphereSetupView

from . import common


class VSphereSetupController(common.BaseVSphereSetupController):
    def render(self):
        self.render_interstitial()
        app.loop.create_task(self.show_vsphere_setup_screen())

    async def show_vsphere_setup_screen(self):
        # Assign current datacenter
        await app.provider.login()
        datacenter = None
        for dc in await app.provider.get_datacenters():
            if dc.name == app.provider.region:
                datacenter = dc
        self.authenticating.clear()
        self.view = VSphereSetupView(datacenter,
                                     self.finish)
        self.view.show()

    def render_interstitial(self):
        self.view = BootstrapWaitView(
            app=app,
            message="Logging in to VSphere. Please wait.")
        app.ui.set_body(self.view)
        self.authenticating.set()
        app.loop.create_task(self._refresh())

    async def _refresh(self):
        while self.authenticating.is_set():
            self.view.redraw_kitt()
            await asyncio.sleep(1)


_controller_class = VSphereSetupController
