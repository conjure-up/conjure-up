from conjureup import controllers
from conjureup.app_config import app
from conjureup.ui.views.regions import RegionPickerView

from . import common


class RegionsController(common.BaseRegionsController):
    def render(self, going_back=False):
        app.log.info('regions[%s]: %s', app.provider.cloud, self.regions)
        if len(self.regions) < 2:
            if going_back:
                return self.back()
            return self.finish(self.default_region)

        view = RegionPickerView(self.regions, self.default_region,
                                self.finish, self.back)
        view.show()

    def back(self):
        return controllers.use('credentials').render(going_back=True)


_controller_class = RegionsController
