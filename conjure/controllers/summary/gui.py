from conjure.ui.views.summary import SummaryView
from conjure.app_config import app
from ubuntui.ev import EventLoop
from . import common


def finish():
    EventLoop.remove_alarms()


def render(results):
    app.log.debug("Rendering summary results: {}".format(results))

    output = common.write_results(results)
    view = SummaryView(app, output)
    app.ui.set_header(title="Deploy Summary",
                      excerpt="Deployment summary for {}".format(
                          app.config['spell']))
    app.ui.set_body(view)
    app.ui.set_footer("Press (Q) to quit.")
    finish()
