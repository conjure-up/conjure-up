from . import common
from conjure import utils


class SummaryController:
    def finish(self):
        return

    def render(self, results):
        common.write_results(results)
        utils.info("\n\nInstallation of your big software is now complete.")
        self.finish()

_controller_class = SummaryController
