from . import common


class VSphereSetupController(common.BaseVSphereSetupController):
    def render(self):
        self.next_screen()


_controller_class = VSphereSetupController
