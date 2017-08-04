from conjureup.app_config import app
from conjureup.ui.views.lxdsetup import LXDSetupView

from . import common


class LXDSetupController(common.BaseLXDSetupController):
    def render(self):
        if len(self.ifaces) == 1:
            return self.setup(self.ifaces[0])

        view = LXDSetupView(app.provider, self.setup)
        view.show()


_controller_class = LXDSetupController
