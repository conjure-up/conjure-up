from ubuntui.views import SelectorWithDescriptionWidget
from ubuntui.ev import EventLoop


class NewModelView(SelectorWithDescriptionWidget):
    def __init__(self, common, cb):
        self.common = common
        self.config = self.common['config']
        title = "Choose a new Juju Model to deploy the solution to"
        models = []
        for p_type in self.config['juju-models'].keys():
            model = self.config['juju-models'][p_type]
            models.append((model['name'], model['description']))
        super().__init__(title, models, cb)

    def cancel(self, btn):
        EventLoop.exit(0)


class ExistingModelView(SelectorWithDescriptionWidget):
    def __init__(self, common, models, cb):
        self.common = common
        self.config = self.common['config']
        title = "Choose an existing Juju Model to deploy the solution to"
        _models = []
        for name in models:
            if name in self.config['juju-models']:
                _model = self.config['juju-models'][name]
                _models.append((_model['name'], _model['description']))
            else:
                _models.append((name, ""))
        super().__init__(title, _models, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
