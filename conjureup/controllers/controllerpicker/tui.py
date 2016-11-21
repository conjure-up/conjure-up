
from conjureup import controllers


class ControllerPicker:

    def finish(self):
        return controllers.use('deploy').render()

    def render(self):
        self.finish()


_controller_class = ControllerPicker
