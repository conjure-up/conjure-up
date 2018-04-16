from ubuntui.ev import EventLoop
from ubuntui.palette import STYLES
from urwid import ExitMainLoop

from conjureup.app_config import app
from conjureup.ui import ConjureUI
from conjureup.ui.views.base import BaseView


class MockupView(BaseView):
    def show(self):
        def _stop(key):
            if key in ['q', 'Q']:
                raise ExitMainLoop()

        app.no_track = True
        app.no_report = True
        app.ui = ConjureUI()
        EventLoop.build_loop(app.ui, STYLES, unhandled_input=_stop)
        super().show()
        EventLoop.run()
