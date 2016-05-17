from conjure.ui.views.bootstrapwait import BootstrapWaitView
from conjure.app_config import app
import sys
from ubuntui.ev import EventLoop

this = sys.modules[__name__]
this.view = None


def __refresh(*args):
    this.view.redraw_kitt()
    EventLoop.set_alarm_in(1, this.__refresh)


def finish():
    pass


def render():
    this.view = BootstrapWaitView(app)
    app.ui.set_header(
        title="Initializing model",
        excerpt="Please wait while Juju bootstraps the model.",
    )
    app.ui.set_body(this.view)
    app.ui.set_subheader("Press (Q) to cancel bootstrap and exit.")
    EventLoop.set_alarm_in(1, __refresh)
