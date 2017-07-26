from conjureup.ui.views.vspheresetup import VSphereSetupView

from . import common


class VSphereSetupController(common.BaseVSphereSetupController):
    def render(self):
        view = VSphereSetupView(self.datacenter,
                                self.finish)
        view.show()


_controller_class = VSphereSetupController
