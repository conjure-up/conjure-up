from . import common
from conjure import utils
from conjure import controllers
from conjure.app_config import app
import os
import sys


this = sys.modules[__name__]
this.bundle = os.path.join(
    app.config['spell-dir'], 'bundle.yaml')
this.bundle_scripts = os.path.join(
    app.config['spell-dir'], 'conjure/steps'
)


def finish(future):
    if future.exception():
        return

    deploy_done_sh = os.path.join(this.bundle_scripts,
                                  '00_deploy-done')

    try:
        common.wait_for_applications(deploy_done_sh,
                                     utils.info)
    except Exception as e:
        utils.error(e)
        sys.exit(1)

    return controllers.use('steps').render()


def render(deploy_future):
    deploy_future.add_done_callback(finish)
