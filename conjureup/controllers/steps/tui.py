from . import common
from collections import OrderedDict
from conjureup import controllers
from conjureup.app_config import app
from conjureup.models.step import StepModel
from conjureup import utils
import os.path as path
import os
import sys
import yaml


class StepsController:
    def __init__(self):
        self.bundle_scripts = path.join(
            app.config['spell-dir'], 'conjure/steps'
        )
        self.steps = common.get_steps(self.bundle_scripts)
        self.results = OrderedDict()

    def finish(self):
        return controllers.use('summary').render(self.results)

    def render(self):
        for step_path in self.steps:
            fname, ext = path.splitext(step_path)
            if not path.isfile(fname) or not os.access(fname, os.X_OK):
                app.log.error(
                    'Unable to process step, missing {}'.format(fname))
                continue
            step_metadata = {}
            with open(step_path) as fp:
                step_metadata = yaml.load(fp.read())
            model = StepModel(step_metadata, step_path)
            model.path = fname
            app.log.debug("Running step: {}".format(model))
            try:
                step_model, _ = common.do_step(model,
                                               None,
                                               utils.info)
                self.results[step_model.title] = step_model.result
            except Exception as e:
                utils.error("Failed to run {}: {}".format(model.path, e))
                sys.exit(1)
        self.finish()

_controller_class = StepsController
