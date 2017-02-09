import os
import os.path as path
from functools import partial

from conjureup import async, controllers, juju
from conjureup.app_config import app
from conjureup.telemetry import track_exception, track_screen
from conjureup.ui.views.deploystatus import DeployStatusView
from ubuntui.ev import EventLoop

from . import common


class DeployStatusController:

    def __init__(self):
        self.view = None
        self.bundle_scripts = path.join(
            app.config['spell-dir'], 'steps'
        )

    def __handle_exception(self, exc):
        track_exception(exc.args[0])
        return app.ui.show_exception_message(exc)

    def __wait_for_applications(self, relations_scheduled_future):
        # do not schedule app wait until all relations are set:
        relations_done_future = relations_scheduled_future.result()
        relations_done_future.result()

        deploy_done_sh = os.path.join(self.bundle_scripts,
                                      '00_deploy-done')

        future = async.submit(partial(common.wait_for_applications,
                                      deploy_done_sh,
                                      app.ui.set_footer),
                              self.__handle_exception,
                              queue_name=juju.JUJU_ASYNC_QUEUE)
        if future:
            future.add_done_callback(self.finish)

    def finish(self, future):
        if not future.exception():
            return controllers.use('steps').render()
        EventLoop.remove_alarms()

    def __refresh(self, *args):
        self.view.refresh_nodes()
        EventLoop.set_alarm_in(1, self.__refresh)

    def render(self, last_deploy_action_future):
        """ Render deploy status view
        """
        track_screen("Deploy Status")
        self.view = DeployStatusView(app)

        try:
            name = app.config['metadata']['friendly-name']
        except KeyError:
            name = app.config['spell']
        app.ui.set_header(
            title="Conjuring up {}".format(
                name)
        )
        app.ui.set_body(self.view)
        self.__refresh()
        if last_deploy_action_future:
            last_deploy_action_future.add_done_callback(
                self.__wait_for_applications)


_controller_class = DeployStatusController
