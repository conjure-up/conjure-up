from conjureup.ui.views.deploystatus import DeployStatusView
from ubuntui.ev import EventLoop
from conjureup.app_config import app
from conjureup import utils
from conjureup import controllers
from conjureup import async
from conjureup import juju
from functools import partial
from . import common
import os.path as path
import os


class DeployStatusController:
    def __init__(self):
        self.view = None
        self.pre_exec_pollinate = False
        self.bundle_scripts = path.join(
            app.config['spell-dir'], 'steps'
        )

    def __handle_exception(self, tag, exc):
        utils.pollinate(app.session_id, tag)
        return app.ui.show_exception_message(exc)

    def __wait_for_applications(self, *args):
        deploy_done_sh = os.path.join(self.bundle_scripts,
                                      '00_deploy-done')

        future = async.submit(partial(common.wait_for_applications,
                                      deploy_done_sh,
                                      app.ui.set_footer),
                              partial(self.__handle_exception, 'ED'),
                              queue_name=juju.JUJU_ASYNC_QUEUE)
        future.add_done_callback(self.finish)

    def finish(self, future):
        if not future.exception():
            return controllers.use('steps').render()
        EventLoop.remove_alarms()

    def __refresh(self, *args):
        self.view.refresh_nodes()
        EventLoop.set_alarm_in(1, self.__refresh)

    def render(self):
        """ Render deploy status view
        """
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
        self.__wait_for_applications()


_controller_class = DeployStatusController
