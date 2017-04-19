from conjureup import events, juju, utils
from conjureup.app_config import app
from conjureup.telemetry import track_event


class Destroy:
    def render(self):
        app.loop.create_task(self.do_destroy(app.argv.model,
                                             app.argv.controller))

    async def do_destroy(self, model, controller):
        track_event("Destroying model", "Destroy", "")
        utils.info("Destroying model {} in controller {}".format(model,
                                                                 controller))
        await juju.destroy_model(controller, model)
        utils.info("Model has been removed")
        events.Shutdown.set(0)


_controller_class = Destroy
