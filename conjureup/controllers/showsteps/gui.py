from operator import attrgetter

from conjureup import controllers, utils
from conjureup.app_config import app
from conjureup.models.addon import AddonModel
from conjureup.ui.views.steps import ShowStepsView
from conjureup.ui.widgets.step import StepForm


class ShowStepsController:
    def __init__(self):
        self.view = None

    def render(self):
        if not app.steps:
            return self.finish()

        self.view = ShowStepsView()
        self.view.show()
        app.loop.create_task(self.show_steps())

    async def show_steps(self):
        steps = app.steps + AddonModel.selected_addons_steps()
        for step in filter(attrgetter('viewable'), steps):
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
        await step.after_input(app.ui.set_footer)

    def finish(self):
        steps = app.steps + AddonModel.selected_addons_steps()
        updates = any(step.bundle_add or step.bundle_remove for step in steps)
        if updates:
            utils.setup_metadata_controller()
        return controllers.use('configapps').render()


_controller_class = ShowStepsController
