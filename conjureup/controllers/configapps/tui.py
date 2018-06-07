from conjureup import controllers, utils
from conjureup.consts import spell_types
from conjureup.app_config import app

from . import common


class ConfigAppsController:
    def render(self):
        app.loop.create_task(common.run_before_config(utils.info,
                                                      self.finish))

    def finish(self):
        if app.metadata.spell_type == spell_types.JUJU:
            controllers.use('bootstrap').render()
        else:
            controllers.use('deploy').render()


_controller_class = ConfigAppsController
