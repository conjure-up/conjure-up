from conjureup import controllers, events
from conjureup.app_config import app
from conjureup.ui.views.steps import RunStepsView

from . import common


class RunStepsController:
    def render(self):
        view = RunStepsView()
        view.show()
        app.loop.create_task(self.run_steps(view))

    async def run_steps(self, view):
        for step in app.steps:
            view.mark_running(step)
            step.result = await common.do_step(step, app.ui.set_footer)
            view.mark_complete(step)
        events.PostDeployComplete.set()
        view.show_summary_button(self.finish)

    def finish(self):
        return controllers.use('summary').render()


_controller_class = RunStepsController
