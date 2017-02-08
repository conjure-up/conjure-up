from ubuntui.frame import Frame  # noqa
from ubuntui.views import ErrorView
from conjureup import async
from conjureup.app_config import app
from ubuntui.ev import EventLoop
import macumba
import errno


class ConjureUI(Frame):

    def show_exception_message(self, ex):

        if isinstance(ex, async.ThreadCancelledException):
            pass
        elif isinstance(ex, macumba.errors.ServerError):
            errmsg = ex.args[1]
        elif hasattr(ex, 'errno') and ex.errno == errno.ENOENT:
            # handle oserror
            errmsg = ex.args[1]
        else:
            errmsg = ex.args[0]
        errmsg += ("\n\n"
                   "Review log messages at ~/.cache/conjure-up/conjure-up.log "
                   "If appropriate, please submit a bug here: "
                   "https://github.com/conjure-up/conjure-up/issues/new")

        async.shutdown()
        EventLoop.remove_alarms()
        self.frame.body = ErrorView(errmsg)
        app.log.exception("Showing dialog for exception:")

    def show_error_message(self, msg):
        self.frame.body = ErrorView(msg)
