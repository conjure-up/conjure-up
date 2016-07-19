from conjure.ui.views.summary import SummaryView
from conjure.app_config import app
from ubuntui.ev import EventLoop
from . import common


class SummaryController:
    def __init__(self):
        self.view = None

    def finish(self):
        EventLoop.remove_alarms()
        EventLoop.exit(0)

    def render(self, results):
        app.log.debug("Rendering summary results: {}".format(results))

        common.write_results(results)
        self.view = SummaryView(app, results, self.finish)
        app.ui.set_header(title="Deploy Summary",
                          excerpt="Deployment summary for {}".format(
                              app.config['spell']))
        app.ui.set_body(self.view)
        app.ui.set_footer("Your big software is deployed, press "
                          "(Q) key to return to shell.")

_controller_class = SummaryController
