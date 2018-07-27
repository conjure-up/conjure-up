from conjureup import events
from conjureup.app_config import app
from conjureup.ui.views.steps import RunStepsView

from . import common


class RunStepsController:
    def render(self):
        view = RunStepsView()
        view.show()
        if app.conjurefile['destroy']:
            app.loop.create_task(self.run_uninstall_steps(view))
        else:
            app.loop.create_task(self.run_steps(view))

    async def run_steps(self, view):
        for step in app.all_steps:
            if not step.has_after_deploy:
                continue
            view.mark_step_running(step)
            step.result = await step.after_deploy(view.set_footer)
            view.mark_step_complete(step)
        common.save_step_results()
        events.PostDeployComplete.set()
        view.mark_complete()

    async def run_uninstall_steps(self, view):
        for step in app.all_steps:
            if not step.has_uninstall:
                continue
            view.mark_step_running(step)
            step.result = await step.uninstall(view.set_footer)
            view.mark_step_complete(step)
        common.save_step_results()
        events.PostDeployComplete.set()
        view.mark_complete()


_controller_class = RunStepsController
