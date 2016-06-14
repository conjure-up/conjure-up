from . import common
from collections import OrderedDict
from conjure import controllers
from conjure.app_config import app
from conjure.models.step import StepModel
from conjure import utils
import os.path as path
import os
import sys
import yaml


this = sys.modules[__name__]


this.bundle_scripts = path.join(
    app.config['spell-dir'], 'conjure/steps'
)
this.steps = common.get_steps(this.bundle_scripts)
this.results = OrderedDict()


def finish():
    return controllers.use('summary').render(this.results)


def render():
    for step_path in this.steps:
        fname, ext = path.splitext(step_path)
        if not path.isfile(fname) or not os.access(fname, os.X_OK):
            app.log.error(
                'Unable to process step, missing {}'.format(fname))
            continue
        step_metadata = {}
        with open(step_path) as fp:
            step_metadata = yaml.load(fp.read())
        model = StepModel(step_metadata)
        model.path = fname
        app.log.debug("Running step: {}".format(model))
        try:
            result = common.do_step(model,
                                    utils.info)
            this.results[result.title] = result.result
        except Exception as e:
            utils.error("Failed to run {}: {}".format(model.path, e))
            sys.exit(1)
    finish()
