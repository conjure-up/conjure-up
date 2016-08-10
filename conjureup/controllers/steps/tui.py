from conjureup.controllers.steps import common
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
            app.config['spell-dir'], 'steps'
        )
        self.step_metas = common.get_step_metadata_filenames(
            self.bundle_scripts)
        self.results = OrderedDict()

    def finish(self):
        return controllers.use('summary').render(self.results)

    def render(self):
        for step_meta_path in self.step_metas:
            step_ex_path, ext = path.splitext(step_meta_path)
            if not path.isfile(step_ex_path) or \
               not os.access(step_ex_path, os.X_OK):
                app.log.error(
                    'Unable to process step, missing {}'.format(step_ex_path))
                continue
            step_metadata = {}
            with open(step_meta_path) as fp:
                step_metadata = yaml.load(fp.read())
            model = StepModel(step_metadata, step_meta_path)
            model.path = step_ex_path
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
