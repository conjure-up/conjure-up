from conjure.ui.views.bootstrapwait import BootstrapWaitView
from conjure.app_config import app
from conjure import controllers
from ubuntui.ev import EventLoop
from conjure import async
from conjure import utils
from functools import partial
import sys

this = sys.modules[__name__]


def __handle_exception(tag, exc):
    utils.pollinate(app.session_id, tag)
    return app.ui.show_exception_message(exc)


def finish(*args):
    return controllers.use('deploystatus').render()


def __wait_for_bootstrap():
    def check():
        is_done = False
        while not is_done:
            if not app.bootstrap.running:
                is_done = True
        return

    f = async.submit(check, partial(__handle_exception, 'ED'))
    f.add_done_callback(finish)


def __refresh(*args):
    this.view.redraw_kitt()
    EventLoop.set_alarm_in(1, __refresh)


def render(deploy_future=None):
    app.log.debug("Rendering bootstrap wait")

    this.view = BootstrapWaitView(
        app=app,
        message="Juju Controller is initializing. Please wait.")
    app.ui.set_header(title="Waiting")
    app.ui.set_body(this.view)
    if deploy_future:
        deploy_future.add_done_callback(finish)
    __refresh()
    __wait_for_bootstrap()
