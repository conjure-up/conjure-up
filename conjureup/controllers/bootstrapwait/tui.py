from conjureup import controllers, events
from conjureup.app_config import app


class BootstrapWaitController:
    def render(self):
        app.loop.create_task(self.wait_for_bootstrap())

    async def wait_for_bootstrap(self):
        await events.Bootstrapped.wait()
        controllers.use('deploy').render()


_controller_class = BootstrapWaitController
