from conjureup.ui.views.bootstrapwait import BootstrapWaitView
from conjureup.app_config import app
from conjureup import controllers
from ubuntui.ev import EventLoop


class BootstrapWaitController:

    def __init__(self):
        self.alarm_handle = None
        self.view = None

    def finish(self, *args):
        if self.alarm_handle:
            EventLoop.remove_alarm(self.alarm_handle)
        return controllers.use('deploystatus').render()

    def __refresh(self, *args):
        self.view.redraw_kitt()
        self.alarm_handle = EventLoop.set_alarm_in(
            1,
            self.__refresh)

    def render(self):
        app.log.debug("Rendering bootstrap wait")

        self.view = BootstrapWaitView(
            app=app,
            message="Juju Controller is initializing. Please wait.")
        app.ui.set_header(title="Waiting")
        app.ui.set_body(self.view)

        app.bootstrap.running.add_done_callback(self.finish)
        self.__refresh()


_controller_class = BootstrapWaitController
