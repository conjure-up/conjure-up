from conjureup import controllers, juju
from conjureup.app_config import app
from conjureup.ui.views.ControllerListView import ControllerListView

from . import common


class ControllerPicker(common.BaseControllerPicker):
    def render(self):
        existing_controllers = juju.get_controllers()['controllers']
        self.check_jaas()

        filtered_controllers = {n: d
                                for n, d in existing_controllers.items()
                                if d['cloud'] == app.provider.cloud}

        if not app.jaas_ok and len(filtered_controllers) == 0:
            return self.finish(None)
        view = ControllerListView(app, filtered_controllers,
                                  self.finish, self.back)
        view.show()

    def back(self):
        controllers.use('providersetup').render(going_back=True)


_controller_class = ControllerPicker
