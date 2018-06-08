from conjureup import controllers
from conjureup.app_config import app

from . import common


class ConfigAppsController:

    def render(self, going_back=False):
        app.loop.create_task(common.run_before_config(lambda _: None,
                                                      self.finish))

    def finish(self):
        return controllers.use('deploy').render()

    def back(self):
        controllers.use('showsteps').render(going_back=True)


_controller_class = ConfigAppsController
