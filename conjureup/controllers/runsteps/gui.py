from conjureup import events
from conjureup.app_config import app
from conjureup.models.addon import AddonModel
from conjureup.ui.views.steps import RunStepsView

from . import common


class RunStepsController:
    def render(self):
        view = RunStepsView()
        view.show()
        app.loop.create_task(self.run_steps(view))

    async def run_steps(self, view):
        steps = app.steps + AddonModel.selected_addons_steps()
        for step in steps:
            view.mark_step_running(step)
            step.result = await step.run(app.ui.set_footer)
            view.mark_step_complete(step)
        common.save_step_results()
        events.PostDeployComplete.set()
        view.mark_complete()


_controller_class = RunStepsController
