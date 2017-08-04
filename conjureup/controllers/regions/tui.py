from conjureup import events, utils
from conjureup.app_config import app

from . import common


class RegionsController(common.BaseRegionsController):
    def render(self):
        if app.provider.region or not self.regions:
            self.finish(app.provider.region)
        elif self.default_region:
            self.finish(self.default_region)
        else:
            utils.warning("You attempted to do an install against a cloud "
                          "that requires a region without specifying one, "
                          "and no default could be determined.  Please "
                          "include a region with the cloud in the form: "
                          "<cloud>/<region>")
            events.Shutdown.set(1)


_controller_class = RegionsController
