import asyncio

from conjureup import events, juju, controllers
from conjureup.app_config import app
from conjureup.telemetry import track_event, track_screen
from conjureup.ui.views.destroy_confirm import DestroyConfirmView
from conjureup.ui.views.interstitial import InterstitialView


class DestroyConfirm:
    def __init__(self):
        self.authenticating = asyncio.Event()
        self.destroying = asyncio.Event()
        self.view = None
        self.deploy_map = None

    async def do_destroy(self, model=None, controller=None):
        track_event("Destroying model", "Destroy", "")
        app.ui.set_footer(
            "Destroying model {} in controller {}".format(model, controller))
        await juju.destroy_model(controller, model)
        app.ui.set_footer(
            "Waiting for model cleanup"
        )
        app.ui.set_footer("")
        return controllers.use('destroy').render()

    async def do_destroy_snap(self):
        """ Only one snap for now
        """
        pass

    def finish(self):
        self.destroying.set()
        view = InterstitialView(title="Destroying Deployment",
                                message="Destroying Deployment. Please wait.",
                                event=self.destroying)
        view.show()

        if self.deploy_map['type'] == 'juju':
            app.loop.create_task(self.do_destroy(
                self.deploy_map['model'], self.deploy_map['controller']))
        elif self.deploy_map['type'] == 'snap':
            app.loop.create_task(self.do_destroy_snap(
                self.deploy_map['snap']
            ))

    def back(self):
        return controllers.use('destroy').render()

    async def login(self, controller, model):
        await juju.connect_model()
        self.authenticating.clear()
        track_screen("Destroy Confirm Model")
        self.view = DestroyConfirmView(self.finish, self.back)
        self.view.show()

    def render_interstitial(self):
        self.authenticating.set()
        view = InterstitialView(title="Controller Login Wait",
                                message="Logging in to model. Please wait.",
                                event=self.authenticating)
        view.show()

    def render(self, selection):
        self.deploy_map = selection
        if self.deploy_map['type'] == 'juju':
            controller = self.deploy_map['controller']
            model = self.deploy_map['model']
            app.provider.controller = controller
            app.provider.model = model
            events.ModelAvailable.set()
            self.authenticating.set()
            self.render_interstitial()
            app.loop.create_task(self.login(controller, model))


_controller_class = DestroyConfirm
