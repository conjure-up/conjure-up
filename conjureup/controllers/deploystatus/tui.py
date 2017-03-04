from conjureup import controllers, utils
from conjureup.app_config import app

from . import common


class DeployStatusController:
    async def finish(self):
        await common.wait_for_applications(utils.info)
        return controllers.use('steps').render()

    def render(self):
        app.loop.create_task(self.finish())


_controller_class = DeployStatusController
