from conjureup import controllers
from conjureup.app_config import app
from conjureup.download import EndpointType
from conjureup.telemetry import track_event
from conjureup.ui.views.addons import AddonsView
from conjureup.utils import setup_metadata_controller


class AddonsController:
    def __init__(self):
        back = self.back
        if app.endpoint_type == EndpointType.LOCAL_DIR:
            back = None
        self.view = AddonsView(self.finish, back)

    def render(self):
        if not app.addons:
            return self.finish()

        self.view.show()

    def finish(self):
        app.selected_addons = self.view.selected
        if app.selected_addons:
            for addon in app.selected_addons:
                track_event("Addon Selected", addon, "")
            # reload the bundle data w/ addons merged
            setup_metadata_controller()
        controllers.use('clouds').render()

    def back(self):
        controllers.use('spellpicker').render()


_controller_class = AddonsController
