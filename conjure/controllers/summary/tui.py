from . import common
from conjure import utils
import sys


class SummaryController:
    def finish(self):
        sys.exit(0)

    def render(self, results):
        common.write_results(results)
        utils.info("\n".join(results))
        self.finish()

_controller_class = SummaryController
