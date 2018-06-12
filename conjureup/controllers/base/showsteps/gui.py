from operator import attrgetter

from conjureup import controllers
from conjureup.app_config import app
from conjureup.ui.views.steps import ShowStepsView
from conjureup.ui.widgets.step import StepForm


class ShowStepsController:
    def __init__(self):
        self.view = None

    def render(self, going_back=False):
        if not app.steps:
            if going_back:
                return self.back()
            else:
                return self.finish()

        self.view = ShowStepsView(None, self.back)
        self.view.show()
        app.loop.create_task(self.show_steps())

    async def show_steps(self):
        for step in filter(attrgetter('viewable'), app.all_steps):
            if not (step.additional_input or step.needs_sudo):
                continue
            if step.cloud_whitelist and app.provider.cloud_type \
               not in step.cloud_whitelist:
                continue
            await self.show_step(step)

        return self.finish()

    async def show_step(self, step):
        step_widget = StepForm(app, step)
        self.view.add_step(step_widget)
        await step_widget.complete.wait()
        if step_widget.sudo_input:
            app.sudo_pass = step_widget.sudo_input.value
        for field in step_widget.fields:
            app.steps_data[step.name][field.key] = field.input.value
        await step.after_input(self.view.set_footer)

    def finish(self):
        if app.has_bundle_modifications:
            controllers.setup_metadata_controller()
        return controllers.use('configapps').render()

    def back(self):
        controllers.use('jaaslogin').render(going_back=True)


_controller_class = ShowStepsController
