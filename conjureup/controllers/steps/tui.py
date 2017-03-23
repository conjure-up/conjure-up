import os.path as path
import sys
from collections import OrderedDict

from conjureup import controllers, utils
from conjureup.app_config import app
from conjureup.controllers.steps import common


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
            try:
                model = common.load_step(step_meta_path)
            except common.ValidationError as e:
                app.log.error(e.msg)
                utils.error(e.msg)
                sys.exit(1)
            if model.needs_sudo and not model.can_sudo():
                utils.error("Step requires passwordless sudo: {}".format(
                    model.title))
                sys.exit(1)
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
