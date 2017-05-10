from conjureup import controllers, events, juju, utils
from conjureup.app_config import app
from conjureup.consts import JAAS_CLOUDS, JAAS_ENDPOINT
from conjureup.telemetry import track_screen
from conjureup.ui.views.ControllerListView import ControllerListView


class ControllerPicker:
    def finish(self, controller):
        if controller is None:
            return controllers.use('clouds').render()

        if controller == 'jaas':
            if not app.jaas_controller or not juju.has_jaas_auth():
                # jaas is either not registered or not logged in
                return controllers.use('jaaslogin').render()
            # jaas already registered, but we they still need to pick a cloud
            app.current_controller = app.jaas_controller
            app.is_jaas = True
            events.Bootstrapped.set()
            return controllers.use('clouds').render()

        app.current_controller = controller
        app.current_model = utils.gen_model()

        c_info = juju.get_controller_info(app.current_controller)
        app.current_cloud = c_info['details']['cloud']

        events.Bootstrapped.set()

        app.loop.create_task(juju.add_model(app.current_model,
                                            app.current_controller,
                                            app.current_cloud))
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
