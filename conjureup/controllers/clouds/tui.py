from pathlib import Path

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

    def render(self):
        utils.info(
            "Summoning {} to {}".format(app.argv.spell, app.provider.cloud))
        if app.provider.cloud_type == cloud_types.LOCALHOST:
            if not Path('/snap/bin/lxc').exists():
                utils.error("Unable to find lxc executable, please make "
                            "sure LXD is installed: `sudo snap install lxd`")
                events.Shutdown.set(1)
        self.finish()


_controller_class = CloudsController
