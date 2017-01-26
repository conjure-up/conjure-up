from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.telemetry import track_exception, track_screen
from conjureup.ui.views.destroy import DestroyView


class Destroy:

    def __init__(self):
        self.view = None

    def __handle_exception(self, exc):
        track_exception(exc.args[0])
        app.ui.show_exception_message(exc)

    def finish(self, controller, model):
        return controllers.use('destroyconfirm').render(controller, model)

    def render(self):
        models_map = {}
        existing_controllers = juju.get_controllers()['controllers']
        for cname, d in existing_controllers.items():
            models_map[cname] = juju.get_models(cname)

        track_screen("Destroy Controller")
        excerpt = ("Press [ENTER] on the highlighted item to destroy")
        view = DestroyView(app,
                           models=models_map,
                           cb=self.finish)

        app.ui.set_header(
            title="Choose a deployment to teardown",
            excerpt=excerpt
        )
        app.ui.set_body(view)


_controller_class = Destroy
