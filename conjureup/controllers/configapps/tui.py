from conjureup import controllers


class ConfigAppsController:
    def render(self):
        return controllers.use('bootstrap').render()


_controller_class = ConfigAppsController
