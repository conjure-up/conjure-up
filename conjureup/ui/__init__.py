from ubuntui.frame import Frame  # noqa
from ubuntui.views import ErrorView
from conjureup import async
from conjureup.app_config import app
from ubuntui.ev import EventLoop
import errno


class ConjureUI(Frame):

    def show_exception_message(self, ex):
        try:
            raise ex
        except type(ex):
            # not sure of a cleaner way to log the exception instance
            app.log.exception(str(ex))

        if isinstance(ex, async.ThreadCancelledException):
            pass
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
        app.log.debug("Showing dialog for exception: {}".format(ex))

    def show_error_message(self, msg):
        self.frame.body = ErrorView(msg)
