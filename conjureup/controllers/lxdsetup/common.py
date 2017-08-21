from conjureup import controllers


class BaseLXDSetupController:
    def next_screen(self):
        return controllers.use('controllerpicker').render()
