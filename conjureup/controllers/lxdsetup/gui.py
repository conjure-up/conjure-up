from conjureup.app_config import app
from conjureup.models.provider import load_schema
from conjureup.ui.views.lxdsetup import LXDSetupView

from . import common


class LXDSetupController(common.LXDSetupController):
    def render(self):
        if self.is_ready:
            return self.next_screen()

        if len(self.ifaces) == 1:
            return self.setup(self.ifaces[0])

        view = LXDSetupView(self.schema, self.setup)
        view.show()

    @property
    def schema(self):
        if hasattr(self, '_schema'):
            return self._schema
        self._schema = load_schema(app.current_cloud_type)
        return self._schema


_controller_class = LXDSetupController
