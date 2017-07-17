from conjureup import controllers, events, juju, utils
from conjureup.app_config import app


class JaaSLoginController:
    def render(self):
        if not app.jaas_ok:
            utils.error('JaaS not compatible with specified cloud')
            return events.Shutdown.set(1)
        if not app.jaas_controller:
            utils.error('No JaaS controller registered')
            return events.Shutdown.set(1)
        if not juju.has_jaas_auth():
            utils.error('JaaS controller not authenticated')
            return events.Shutdown.set(1)
        app.is_jaas = True
        events.Bootstrapped.set()
        app.loop.create_task(juju.add_model(app.current_model,
                                            app.current_controller,
                                            app.current_cloud))
        controllers.use('showsteps').render()


_controller_class = JaaSLoginController
