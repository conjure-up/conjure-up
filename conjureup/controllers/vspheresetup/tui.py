from conjureup import controllers

from . import common


class VSphereSetupController(common.BaseVSphereSetupController):
    def render(self):
        return controllers.use('controllerpicker').render()


_controller_class = VSphereSetupController
