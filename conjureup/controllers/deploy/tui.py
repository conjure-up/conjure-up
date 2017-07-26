from conjureup import controllers, utils
from conjureup.app_config import app

from . import common


class DeployController:
    def render(self):
        app.loop.create_task(common.do_deploy(utils.info))
        app.loop.create_task(self._wait_for_applications())

    async def _wait_for_applications(self):
        await common.wait_for_applications(utils.info)
        return controllers.use('runsteps').render()


_controller_class = DeployController
