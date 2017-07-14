from conjureup import controllers, events, utils
from conjureup.app_config import app

from . import common


class RunStepsController:
    def render(self):
        app.loop.create_task(self.run_steps())

    async def run_steps(self):
        for step in app.steps:
            step.result = await common.do_step(step, utils.info)
        events.PostDeployComplete.set()
        return controllers.use('summary').render()


_controller_class = RunStepsController
