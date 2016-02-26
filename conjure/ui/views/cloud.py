from ubuntui.views import SelectorWidget
from ubuntui.ev import EventLoop


class CloudView(SelectorWidget):
    def __init__(self, common, models, cb):
        self.common = common
        self.config = self.common['config']
        title = "Choose a cloud to deploy the solution to"
        _models = []
        for name in models:
            _models.append(name)
        super().__init__(title, _models, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
