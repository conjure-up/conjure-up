from conjureup import controllers, utils
from conjureup.app_config import app

from . import common


class ConfigAppsController:
    def render(self):
        app.loop.create_task(common.run_before_config(utils.info,
                                                      self.finish))

    def finish(self):
        controllers.use('bootstrap').render()


_controller_class = ConfigAppsController
