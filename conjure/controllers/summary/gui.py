from conjure.ui.views.summary import SummaryView
from conjure.app_config import app
from ubuntui.ev import EventLoop
from . import common


def finish():
    EventLoop.remove_alarms()
    EventLoop.exit(0)


def render(results):
    app.log.debug("Rendering summary results: {}".format(results))

    common.write_results(results)
    view = SummaryView(app, results, finish)
    app.ui.set_header(title="Deploy Summary",
                      excerpt="Deployment summary for {}".format(
                          app.config['spell']))
    app.ui.set_body(view)
    app.ui.set_footer("Your big software is deployed, press "
                      "(Q) key to return to shell.")
