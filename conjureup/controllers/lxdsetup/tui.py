from . import common


class LXDSetupController(common.BaseLXDSetupController):
    def render(self):
        # can't ask, so pick the first (by name) physical interface we find
        self.setup(self.ifaces[0])


_controller_class = LXDSetupController
