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

    def keypress(self, size, key):
        if key in ['tab', 'shift tab']:
            self._swap_focus()
        return super().keypress(size, key)

    def _swap_focus(self):
        w_count = len(self._w.body.contents) - 1
        if self._w.body.focus_position >= 2 and \
           self._w.body.focus_position < w_count:
            self._w.body.focus_position = w_count
        else:
            self._w.body.focus_position = 2

    def cancel(self, btn):
        EventLoop.exit(0)
