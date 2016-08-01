from conjureup.app_config import app
from conjureup.controllers.summary import common
from conjureup import utils

import os


class SummaryController:
    def __init__(self):
        self.save_path = os.path.join(app.config['spell-dir'],
                                      'results.txt')

    def render(self, results):
        common.write_results(results, self.save_path)
        utils.info("Installation of your big software is now complete.")

_controller_class = SummaryController
