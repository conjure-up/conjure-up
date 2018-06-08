from conjureup import controllers, juju, utils
from conjureup.app_config import app
from conjureup.consts import JAAS_CLOUDS, JAAS_ENDPOINT


class BaseControllerPicker:
    def check_jaas(self):
        existing_controllers = juju.get_controllers()['controllers']

        app.jaas_ok = app.provider.cloud_type in JAAS_CLOUDS
        jaas_controller = {n for n, c in existing_controllers.items()
                           if JAAS_ENDPOINT in c['api-endpoints']}
        if jaas_controller:
            app.jaas_controller = jaas_controller.pop()

    def finish(self, controller):
        if controller is None:
            app.provider.controller = "conjure-up-{}-{}".format(
                app.provider.cloud,
                utils.gen_hash())
        else:
            app.provider.controller = controller

        if controller == 'jaas':
            if not app.jaas_controller or not juju.has_jaas_auth():
                # jaas is either not registered or not logged in
                return controllers.use('jaaslogin').render()
            # jaas already registered
            app.provider.controller = app.jaas_controller
            app.is_jaas = True
        return controllers.use('showsteps').render()
