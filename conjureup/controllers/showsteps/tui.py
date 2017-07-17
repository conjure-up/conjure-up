from conjureup import controllers
from conjureup.controllers.showsteps import common


class ShowStepsController:
    def render(self):
        common.load_steps()
        controllers.use('deploy').render()


_controller_class = ShowStepsController
