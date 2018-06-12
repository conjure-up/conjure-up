from conjureup import controllers
from conjureup.controllers.base.addons.gui import AddonsController


class SnapAddonsController(AddonsController):
    def next_screen(self):
        controllers.use('showsteps').render()


_controller_class = SnapAddonsController
