import asyncio

from conjureup import controllers, events, juju
from conjureup.app_config import app
from conjureup.telemetry import track_event, track_screen
from conjureup.ui.views.bootstrapwait import BootstrapWaitView
from conjureup.ui.views.destroy_confirm import DestroyConfirmView


class DestroyConfirm:
    def __init__(self):
        self.authenticating = asyncio.Event()
        self.view = None

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

    async def login(self, controller, model):
        await juju.login()
        self.authenticating.clear()
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

    def render_interstitial(self):
        track_screen("Controller Login Wait")
        app.ui.set_header(title="Waiting")
        self.view = BootstrapWaitView(
            app=app,
            message="Logging in to model. Please wait.")
        app.ui.set_body(self.view)
        self.authenticating.set()
        app.loop.create_task(self._refresh())
        self._refresh()

    async def _refresh(self):
        while self.authenticating.is_set():
            self.view.redraw_kitt()
            await asyncio.sleep(1)

    def render(self, controller, model):
        app.provider.controller = controller
        app.provider.model = model['name']
        events.ModelAvailable.set()
        self.authenticating.set()
        self.render_interstitial()
        app.loop.create_task(self.login(controller, model))


_controller_class = DestroyConfirm
