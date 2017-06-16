from conjureup import controllers, events, juju, utils
from conjureup.app_config import app
from conjureup.consts import JAAS_CLOUDS, JAAS_ENDPOINT


class BaseControllerPicker:
    def check_jaas(self):
        existing_controllers = juju.get_controllers()['controllers']

        app.jaas_ok = app.current_cloud_type in JAAS_CLOUDS
        jaas_controller = {n for n, c in existing_controllers.items()
                           if JAAS_ENDPOINT in c['api-endpoints']}
        if jaas_controller:
            app.jaas_controller = jaas_controller.pop()

    def finish(self, controller):
        if controller is None:
            app.current_controller = "conjure-up-{}-{}".format(
                app.current_cloud,
                utils.gen_hash())
            return controllers.use('bootstrap').render()

        if controller == 'jaas':
            if not app.jaas_controller or not juju.has_jaas_auth():
                # jaas is either not registered or not logged in
                return controllers.use('jaaslogin').render()
            # jaas already registered
            app.current_controller = app.jaas_controller
            app.is_jaas = True
        else:
            app.current_controller = controller

        if app.current_controller not in juju.get_controllers():
            return controllers.use('bootstrap').render()

        c_info = juju.get_controller_info(app.current_controller)
        if c_info['details']['cloud']:
            app.current_cloud = c_info['details']['cloud']

        events.Bootstrapped.set()

        app.loop.create_task(juju.add_model(app.current_model,
                                            app.current_controller,
                                            app.current_cloud))
        return controllers.use('deploy').render()
