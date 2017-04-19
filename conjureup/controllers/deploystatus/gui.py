import asyncio

from conjureup import controllers, events
from conjureup.app_config import app
from conjureup.telemetry import track_screen
from conjureup.ui.views.deploystatus import DeployStatusView

from . import common


class DeployStatusController:
    async def _wait_for_applications(self):
        await common.wait_for_applications(app.ui.set_footer)
        controllers.use('steps').render()

    async def _refresh(self, view):
        await events.ModelConnected.wait()
        while not events.ModelSettled.is_set():
            view.refresh_nodes(app.juju.client.applications)
            await asyncio.sleep(1)

    def render(self):
        """ Render deploy status view
        """
        track_screen("Deploy Status")
        view = DeployStatusView(app)

        try:
            name = app.config['metadata']['friendly-name']
        except KeyError:
            name = app.config['spell']
        app.ui.set_header(title="Conjuring up {}".format(name))
        app.ui.set_body(view)
        app.loop.create_task(self._refresh(view))
        app.loop.create_task(self._wait_for_applications())


_controller_class = DeployStatusController
