from conjureup import controllers
from conjureup.app_config import app
from conjureup.download import EndpointType
from conjureup.telemetry import track_event
from conjureup.ui.views.addons import AddonsView


class AddonsController:
    def render(self, going_back=False):
        if not app.addons:
            if going_back:
                return self.prev_screen()
            else:
                return self.next_screen()

        prev_screen = self.prev_screen
        if app.endpoint_type == EndpointType.LOCAL_DIR:
            prev_screen = None
        self.view = AddonsView(self.finish, prev_screen)
        self.view.show()

    def finish(self):
        app.selected_addons = self.view.selected
        if app.selected_addons:
            for addon in app.selected_addons:
                track_event("Addon Selected", addon, "")
            # reload the bundle data w/ addons merged
            controllers.setup_metadata_controller()
        self.next_screen()

    def next_screen(self):
        controllers.use('clouds').render()

    def prev_screen(self):
        controllers.use('spellpicker').render()


_controller_class = AddonsController
