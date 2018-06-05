import asyncio

from juju.utils import run_with_interrupt

from conjureup import controllers, errors, events, juju, utils
from conjureup.app_config import app
from conjureup.consts import CUSTOM_PROVIDERS
from conjureup.models.provider import Localhost as LocalhostProvider
from conjureup.models.provider import (
    LocalhostError,
    LocalhostJSONError,
    SchemaErrorUnknownCloud,
    load_schema
)
from conjureup.telemetry import track_event
from conjureup.ui.views.cloud import CloudView

from .common import BaseCloudController


class CloudsController(BaseCloudController):
    cancel_monitor = asyncio.Event()

    def __init__(self):
        self.view = None

    def finish(self, cloud):
        """ Load the selected cloud provider
        """
        self.cancel_monitor.set()

        if cloud in CUSTOM_PROVIDERS:
            app.provider = load_schema(cloud)
        else:
            app.provider = load_schema(juju.get_cloud_types_by_name()[cloud])

        try:
            app.provider.load(cloud)
        except SchemaErrorUnknownCloud:
            app.provider.cloud = utils.gen_cloud()

        if app.provider.model is None:
            app.provider.model = utils.gen_model()

        track_event("Cloud selection", app.provider.cloud, "")

        return controllers.use('credentials').render()

    def render(self, going_back=False):
        "Pick or create a cloud to bootstrap a new controller on"
        all_clouds = juju.get_clouds()
        compatible_clouds = juju.get_compatible_clouds()
        cloud_types = juju.get_cloud_types_by_name()
        # filter to only public clouds
        public_clouds = sorted(
            name for name, info in all_clouds.items()
            if info['defined'] == 'public')
        # filter to custom clouds
        # exclude localhost because we treat that as "configuring a new cloud"
        custom_clouds = sorted(
            name for name, info in all_clouds.items()
            if info['defined'] != 'public' and
            cloud_types[name] != 'localhost')

        prev_screen = self.prev_screen
        if app.alias_given or (app.spell_given and not app.addons):
            # we were given an alias (so spell and addons are locked)
            # or we were given a spell and there are no addons to change
            # so we disable the back button
            prev_screen = None
        self.view = CloudView(app,
                              public_clouds,
                              custom_clouds,
                              compatible_clouds,
                              cb=self.finish,
                              back=prev_screen)

        if 'localhost' in compatible_clouds:
            app.log.debug(
                "Starting watcher for verifying LXD server is available.")
            self.cancel_monitor.clear()
            app.loop.create_task(
                self._monitor_localhost(
                    LocalhostProvider(),
                    self.view._enable_localhost_widget
                )
            )
        self.view.show()

    async def _monitor_localhost(self, provider, cb):
        """ Checks that localhost/lxd is available and listening,
        updates widget accordingly
        """

        while not self.cancel_monitor.is_set():
            try:
                provider._set_lxd_dir_env()
                client_compatible = await provider.is_client_compatible()
                server_compatible = await provider.is_server_compatible()
                if client_compatible and server_compatible:
                    events.LXDAvailable.set()
                    self.cancel_monitor.set()
                    cb()
                    return
            except (LocalhostError, LocalhostJSONError,
                    errors.LocalhostLXDBinaryNotFound,
                    FileNotFoundError):
                pass
            await run_with_interrupt(asyncio.sleep(2),
                                     self.cancel_monitor)

    def prev_screen(self):
        self.cancel_monitor.set()
        controllers.use('addons').render(going_back=True)


_controller_class = CloudsController
