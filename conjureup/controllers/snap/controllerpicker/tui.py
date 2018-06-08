from conjureup.app_config import app

from . import common


class ControllerPicker(common.BaseControllerPicker):
    def render(self):
        self.check_jaas()
        self.finish(app.conjurefile['controller'])


_controller_class = ControllerPicker
