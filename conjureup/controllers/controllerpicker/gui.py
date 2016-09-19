import petname

from conjureup import async, controllers, juju, utils
from conjureup.app_config import app
from conjureup.ui.views.ControllerListView import ControllerListView


class ControllerPicker:

    def __init__(self):
        self.view = None

    def __handle_exception(self, exc):
        utils.pollinate(app.session_id, "E004")
        app.ui.show_exception_message(exc)

    def __add_model(self):
        juju.switch_controller(app.current_controller)
        juju.add_model(app.current_model)
        juju.switch_model(app.current_model)

    def finish(self, controller):
        utils.pollinate(app.session_id, 'CS')
        if controller is None:
            return controllers.use('clouds').render()

        app.current_controller = controller
        app.current_model = petname.Name()
        async.submit(self.__add_model,
                     self.__handle_exception,
                     queue_name=juju.JUJU_ASYNC_QUEUE)

        return controllers.use('deploy').render()

    def render(self):
        existing_controllers = juju.get_controllers()['controllers']
        if len(existing_controllers) == 0:
            return controllers.use('clouds').render()

        excerpt = app.config.get(
            'description',
            "Please select an existing controller,"
            " or choose to bootstrap a new one.")
        view = ControllerListView(app,
                                  controllers,
                                  self.finish)

        app.ui.set_header(
            title="Choose a Controller or Create new",
            excerpt=excerpt
        )
        app.ui.set_body(view)

_controller_class = ControllerPicker
