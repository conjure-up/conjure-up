from . import common
from conjure import utils
from conjure import controllers
from conjure.app_config import app
from glob import glob
import os
import sys

this = sys.modules[__name__]
this.results = []


def __fatal(error):
    utils.error(error)
    sys.exit(1)


def finish():
    bundle_scripts = os.path.join(
        app.config['spell-dir'], 'conjure/steps'
    )

    # post step processing
    steps = sorted(glob(os.path.join(bundle_scripts, 'step-*.sh')))
    common.wait_for_steps(steps, utils.info, __fatal)

    return controllers.use('summary').render(this.results)


def render():
    finish()
