from conjureup import controllers
from conjureup.app_config import app
from conjureup.telemetry import track_screen
from conjureup.ui.views.addons import AddonsView


class AddonsController:
    def __init__(self):
        self.view = AddonsView(self.finish, self.back)

    def render(self):
        if not self.view.choices:
            return self.finish()

        track_screen('Addons')
        self.view.show()

    def finish(self):
        app.addons = self.view.selected
        controllers.use('clouds').render()

    def back(self):
        controllers.use('spellpicker').render()


_controller_class = AddonsController
