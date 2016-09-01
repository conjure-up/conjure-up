import os
import sys
from functools import partial

from conjureup import async, controllers, juju, utils
from conjureup.app_config import app

from . import common


class DeployStatusController:

    def __init__(self):
        self.bundle_scripts = os.path.join(
            app.config['spell-dir'], 'steps'
        )

    def __handle_exception(self, tag, exc):
        utils.pollinate(app.session_id, tag)
        utils.error(exc)
        sys.exit(1)

    def finish(self, future):
        if not future.exception():
            return controllers.use('steps').render()

    def render(self):
        deploy_done_sh = os.path.join(self.bundle_scripts,
                                      '00_deploy-done')
        future = async.submit(partial(common.wait_for_applications,
                                      deploy_done_sh,
                                      utils.info),
                              partial(self.__handle_exception, 'ED'),
                              queue_name=juju.JUJU_ASYNC_QUEUE)
        future.add_done_callback(self.finish)

_controller_class = DeployStatusController
