from conjure.ui.views.bootstrapwait import BootstrapWaitView
from ubuntui.ev import EventLoop


class TUI:
    def __init__(self, app):
        self.app = app

    def finish(self):
        self.app.log.debug("TUI finish")

    def render(self):
        self.app.log.debug("TUI render")


class GUI:
    def __init__(self, app):
        self.app = app

    def refresh(self, *args):
        self.view.redraw_kitt()
        EventLoop.set_alarm_in(1, self.refresh)

    def finish(self):
        pass

    def render(self):
        self.view = BootstrapWaitView(self.app)
        self.app.ui.set_header(
            title="Initializing model",
            excerpt="Please wait while Juju bootstraps the model.",
        )
        self.app.ui.set_body(self.view)
        self.app.ui.set_subheader("Press (Q) to cancel bootstrap and exit.")
        EventLoop.set_alarm_in(1, self.refresh)


def load_bootstrapwait_controller(app):
    if app.headless:
        return TUI(app)
    else:
        return GUI(app)
