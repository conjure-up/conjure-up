from ubuntui.views import SelectorWidget
from ubuntui.ev import EventLoop


class CloudView(SelectorWidget):
    def __init__(self, common, clouds, cb):
        self.common = common
        self.config = self.common['config']
        title = "Clouds"
        _clouds = []
        for name in clouds:
            _clouds.append(name)
        super().__init__(title, _clouds, cb)

    def cancel(self, btn):
        EventLoop.exit(0)
