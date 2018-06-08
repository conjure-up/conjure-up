from conjureup import controllers
from conjureup.controllers.showsteps.gui import ShowStepsController


class SnapShowStepsController(ShowStepsController):
    def finish(self):
        return controllers.use('configapps').render()

    def back(self):
        controllers.use('spellpick').render()


_controller_class = SnapShowStepsController
