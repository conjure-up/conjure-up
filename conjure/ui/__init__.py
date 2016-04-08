from ubuntui.frame import Frame  # noqa
from ubuntui.views import ErrorView
from conjure import async
from ubuntui.ev import EventLoop
import errno


class ConjureUI(Frame):
    def show_exception_message(self, ex):
        if isinstance(ex, async.ThreadCancelledException):
            pass
        elif hasattr(ex, 'errno') and ex.errno == errno.ENOENT:
            # handle oserror
            self.frame.body = ErrorView(ex.args[1])
        else:
            self.frame.body = ErrorView(ex.args[0])

        EventLoop.remove_alarms()

    def show_error_message(self, msg):
        self.frame.body = ErrorView(msg)
