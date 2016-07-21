from . import common
from conjure import utils


class SummaryController:
    def render(self, results):
        common.write_results(results)
        utils.info("Installation of your big software is now complete.")

_controller_class = SummaryController
