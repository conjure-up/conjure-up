from pathlib import Path

from ubuntui.ev import EventLoop
from ubuntui.frame import Frame  # noqa
from ubuntui.views import ErrorView
from urwid import Overlay

from conjureup import async
from conjureup.app_config import app
from conjureup.ui.views.shutdown import ShutdownView


class ConjureUI(Frame):

    def show_exception_message(self, ex):
        _cache_dir = Path(app.conjurefile['cache-dir']) / 'conjure-up.log'
        errmsg = str(ex)
        errmsg += (
            "\n\n Review log messages at {} "
            "If appropriate, please submit a bug here: "
            "https://github.com/conjure-up/conjure-up/issues/new".format(
                _cache_dir))

        async.shutdown()
        EventLoop.remove_alarms()
        self.frame.body = ErrorView(errmsg)
        # ensure error is shown, even if exception was inside urwid
        EventLoop.redraw_screen()
        app.log.debug("Showing dialog for exception: {}".format(ex))

    def show_error_message(self, msg):
        self.frame.body = ErrorView(msg)

    def show_shutdown_dialog(self, exit_code):
        self.frame.body = Overlay(ShutdownView(exit_code),
                                  self.frame.body,
                                  'center', ('relative', 45),
                                  'middle', 'pack')

    def hide_shutdown_dialog(self):
        self.frame.body = self.frame.body.bottom_w

    def quit(self, exit_code=0):
        self.show_shutdown_dialog(exit_code)
