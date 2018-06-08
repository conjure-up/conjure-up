from conjureup import controllers


class ShowStepsController:
    def render(self):
        controllers.use('configapps').render()


_controller_class = ShowStepsController
