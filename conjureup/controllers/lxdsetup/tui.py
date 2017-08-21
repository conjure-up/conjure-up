from . import common


class LXDSetupController(common.BaseLXDSetupController):
    def render(self):
        return self.next_screen()


_controller_class = LXDSetupController
