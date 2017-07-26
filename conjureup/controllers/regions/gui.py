from conjureup import controllers
from conjureup.ui.views.regions import RegionPickerView

from . import common


class RegionsController(common.BaseRegionsController):
    def render(self, back=False):
        if len(self.regions) < 2:
            if back:
                return self.back()
            return self.finish(self.default_region)

        view = RegionPickerView(self.regions, self.default_region,
                                self.finish, self.back)
        view.show()

    def back(self):
        return controllers.use('credentials').render()


_controller_class = RegionsController
