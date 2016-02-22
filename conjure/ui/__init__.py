from ubuntui.frame import Frame  # noqa
from ubuntui.views import ErrorView
from conjure import async
from ubuntui.ev import EventLoop


class ConjureUI(Frame):
    key_conversion_map = {'tab': 'down', 'shift tab': 'up'}

    def show_exception_message(self, ex):
        if isinstance(ex, async.ThreadCancelledException):
            pass
        else:
            self.frame.body = ErrorView(ex.args[0])

        EventLoop.remove_alarms()

    def show_error_message(self, msg):
        self.frame.body = ErrorView(msg)

    def keypress(self, size, key):
        key = self.key_conversion_map.get(key, key)
        return super().keypress(size, key)
