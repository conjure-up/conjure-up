import asyncio

from conjureup import events, juju
from conjureup.app_config import app
from conjureup.telemetry import track_event, track_screen
from conjureup.ui.views.destroy_confirm import DestroyConfirmView
from conjureup.ui.views.interstitial import InterstitialView
from conjureup.controllers.base.destroy import gui


class DestroyConfirm:
    def __init__(self):
        self.authenticating = asyncio.Event()

    async def do_destroy(self, model, controller):
        track_event("Destroying model", "Destroy", "")
        app.ui.set_footer(
            "Destroying model {} in controller {}".format(model, controller))
        await juju.destroy_model(controller, model)
        app.ui.set_footer("")
        gui.Destroy().render(show_snaps=False)

    def finish(self, controller_name=None, model_name=None):
        if controller_name and model_name:
            app.loop.create_task(self.do_destroy(model_name, controller_name))
        else:
            gui.Destroy().render(show_snaps=False)

    async def login(self, controller, model):
        await juju.connect_model()
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
        self.authenticating.set()
        view = InterstitialView(title="Controller Login Wait",
                                message="Logging in to model. Please wait.",
                                event=self.authenticating)
        view.show()

    def render(self, controller, model):
        app.provider.controller = controller
        app.provider.model = model
        events.ModelAvailable.set()
        self.authenticating.set()
        self.render_interstitial()
        app.loop.create_task(self.login(controller, model))


_controller_class = DestroyConfirm
