from ubuntui.views import SelectorWithDescriptionWidget
from ubuntui.ev import EventLoop


class NewModelView(SelectorWithDescriptionWidget):
    def __init__(self, common, cb):
        self.common = common
        title = "Choose a model to deploy the solution to"
        models = []
        for p in self.common['juju-models']:
            models.append((p.name, p.description))
        super().__init__(title, models, cb)

    def cancel(self, btn):
        EventLoop.exit(0)


class ExistingModelView(SelectorWithDescriptionWidget):
    def __init__(self, common, models, cb):
        self.common = common
        title = "Choose an existing model to deploy the solution to"
        _models = []
        for name in models:
            _models.append((name, ""))
        super().__init__(title, models, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
