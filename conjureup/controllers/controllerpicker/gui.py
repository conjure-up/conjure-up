from conjureup import juju
from conjureup.app_config import app
from conjureup.telemetry import track_screen
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

        track_screen("Controller Picker")
        excerpt = app.config.get(
            'description',
            "Please select an existing controller,"
            " or choose to bootstrap a new one.")
        view = ControllerListView(app,
                                  filtered_controllers,
                                  self.finish)

        app.ui.set_header(
            title="Choose a Controller or Create new",
            excerpt=excerpt
        )
        app.ui.set_body(view)


_controller_class = ControllerPicker
