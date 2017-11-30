from ubuntui.frame import Frame  # noqa
from ubuntui.views import ErrorView
from conjureup import async
from conjureup.app_config import app
from conjureup.ui.views.shutdown import ShutdownView
from ubuntui.ev import EventLoop
from pathlib import Path


class ConjureUI(Frame):

    def show_exception_message(self, ex):
        _cache_dir = Path(app.argv.cache_dir) / 'conjure-up.log'
        errmsg = str(ex)
        errmsg += (
            "\n\n Review log messages at {} "
            "If appropriate, please submit a bug here: "
            "https://github.com/conjure-up/conjure-up/issues/new".format(
                _cache_dir))

        async.shutdown()
        EventLoop.remove_alarms()
        self.frame.body = ErrorView(errmsg)
        app.log.debug("Showing dialog for exception: {}".format(ex))

    def show_error_message(self, msg):
        self.frame.body = ErrorView(msg)

    def show_shutdown_message(self):
        self.frame.body = ShutdownView()
