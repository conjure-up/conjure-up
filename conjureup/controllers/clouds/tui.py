from conjureup import controllers, events, juju, utils
from conjureup.app_config import app
from conjureup.consts import cloud_types

from .common import BaseCloudController


class CloudsController(BaseCloudController):
    def __controller_exists(self, controller):
        return juju.get_controller(controller) is not None

    def finish(self):
        if app.argv.model:
            app.provider.model = app.argv.model
        else:
            app.provider.model = utils.gen_model()

        return controllers.use('credentials').render()

    async def _check_lxd_compat(self):
        utils.info(
            "Summoning {} to {}".format(app.argv.spell, app.provider.cloud))
        if app.provider.cloud_type == cloud_types.LOCALHOST:

            try:
                app.provider._set_lxd_dir_env()
                client_compatible = await app.provider.is_client_compatible()
                server_compatible = await app.provider.is_server_compatible()
                if client_compatible and server_compatible:
                    return self.finish()
                else:
                    utils.error("LXD Server or LXC client not compatible")
                    events.Shutdown.set(1)
            except app.provider.LocalhostError:
                raise
            self.finish()

    def render(self):
        app.loop.create_task(self._check_lxd_compat())


_controller_class = CloudsController
