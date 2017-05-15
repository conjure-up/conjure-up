from . import common


class LXDSetupController(common.LXDSetupController):
    def render(self):
        if self.is_ready:
            return self.next_screen()

        # can't ask, so pick the first (by name) physical interface we find
        self.setup(self.ifaces[0])


_controller_class = LXDSetupController
