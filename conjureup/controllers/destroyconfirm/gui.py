from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.telemetry import track_event, track_exception, track_screen
from conjureup.ui.views.destroy_confirm import DestroyConfirmView
from ubuntui.ev import EventLoop


class DestroyConfirm:

    def __init__(self):
        self.view = None

    def __handle_exception(self, exc):
        track_exception(exc.args[0])
        app.ui.set_footer("Problem destroying the deployment")
        return app.ui.show_exception_message(exc)

    def __do_destroy(self, controller_name, model_name):
        track_event("Destroying model", "Destroy", "")
        app.ui.set_footer("Destroying {} deployment, please wait.".format(
            model_name))
        future = juju.destroy_model_async(controller=controller_name,
                                          model=model_name,
                                          exc_cb=self.__handle_exception)
        if future:
            future.add_done_callback(self.__handle_destroy_done)

    def __handle_destroy_done(self, future):
        if not future.exception():
            app.ui.set_footer("")
            return controllers.use('destroy').render()
        EventLoop.remove_alarms()

    def finish(self, controller_name=None, model_name=None):
        if controller_name and model_name:
            self.__do_destroy(controller_name, model_name)
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
