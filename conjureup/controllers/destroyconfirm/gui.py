from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.telemetry import track_event, track_screen
from conjureup.ui.views.destroy_confirm import DestroyConfirmView


class DestroyConfirm:
    async def do_destroy(self, model, controller):
        track_event("Destroying model", "Destroy", "")
        app.ui.set_footer(
            "Destroying model {} in controller {}".format(model, controller))
        await juju.destroy_model(controller, model)
        app.ui.set_footer("")
        controllers.use('destroy').render()

    def finish(self, controller_name=None, model_name=None):
        if controller_name and model_name:
            app.loop.create_task(self.do_destroy(model_name, controller_name))
        else:
            return controllers.use('destroy').render()

    def render(self, controller, model):
        app.current_controller = controller
        app.current_model = model['name']

        track_screen("Destroy Confirm Model")
        view = DestroyConfirmView(app,
                                  controller,
                                  model,
                                  cb=self.finish)
        app.ui.set_header(
            title="Destroy Confirmation",
            excerpt="Are you sure you wish to destroy the deployment?"
        )
        app.ui.set_body(view)


_controller_class = DestroyConfirm
