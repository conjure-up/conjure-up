from conjureup import async, controllers, juju, utils
from conjureup.app_config import app
from conjureup.consts import JAAS_CLOUDS, JAAS_ENDPOINT
from conjureup.telemetry import track_exception, track_screen
from conjureup.ui.views.ControllerListView import ControllerListView


class ControllerPicker:

    def __init__(self):
        self.view = None

    def __handle_exception(self, exc):
        track_exception(exc.args[0])
        return app.ui.show_exception_message(exc)

    def __add_model(self):
        juju.add_model(app.current_model,
                       app.current_controller,
                       app.current_cloud)

    def finish(self, controller):
        if controller is None:
            return controllers.use('clouds').render()

        if controller == 'jaas':
            return controllers.use('jaaslogin').render()

        app.current_controller = controller
        app.current_model = "conjure-up-{}-{}".format(
            app.env['CONJURE_UP_SPELL'],
            utils.gen_hash())

        try:
            c_info = juju.get_controller_info(app.current_controller)
        except Exception as e:
            return self.__handle_exception(e)
        app.current_cloud = c_info['details']['cloud']

        async.submit(self.__add_model,
                     self.__handle_exception,
                     queue_name=juju.JUJU_ASYNC_QUEUE)
        return controllers.use('deploy').render()

    def render(self):
        existing_controllers = juju.get_controllers()['controllers']
        clouds = juju.get_compatible_clouds()
        cloud_types = juju.get_cloud_types_by_name()

        app.jaas_ok = set(clouds) & JAAS_CLOUDS
        jaas_controller = {n for n, c in existing_controllers.items()
                           if JAAS_ENDPOINT in c['api-endpoints']}
        if jaas_controller:
            app.jaas_controller = jaas_controller.pop()

        filtered_controllers = {n: d
                                for n, d in existing_controllers.items()
                                if cloud_types.get(d['cloud']) in clouds}

        if not app.jaas_ok and len(filtered_controllers) == 0:
            return controllers.use('clouds').render()

        track_screen("Controller Picker")
        excerpt = app.config.get(
            'description',
            "Please select an existing controller,"
            " or choose to bootstrap a new one.")
        view = ControllerListView(app,
                                  filtered_controllers,
                                  self.finish)

        app.ui.set_header(
            title="Choose a Controller or Create new",
            excerpt=excerpt
        )
        app.ui.set_body(view)


_controller_class = ControllerPicker
