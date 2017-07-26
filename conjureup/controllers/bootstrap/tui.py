from functools import partial

from conjureup import controllers, events, utils
from conjureup.app_config import app

from . import common


class BootstrapController(common.BaseBootstrapController):
    msg_cb = partial(utils.info)

    def render(self):
        if app.is_jaas or self.is_existing_controller():
            app.loop.create_task(self.do_add_model())
        else:
            app.loop.create_task(self.do_bootstrap())
        app.loop.create_task(self.wait())

    async def wait(self):
        await events.Bootstrapped.wait()
        controllers.use('deploy').render()


_controller_class = BootstrapController
