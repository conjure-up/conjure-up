from conjure.ui.views.summary import SummaryView
from conjure.app_config import app
from ubuntui.ev import EventLoop
from . import common


def finish():
    EventLoop.remove_alarms()


def render(results):
    app.log.debug("Rendering summary results: {}".format(results))

    common.write_results(results)
    view = SummaryView(app, results)
    app.ui.set_header(title="Deploy Summary")
    app.ui.set_body(view)
    app.ui.set_footer("Press (Q) to quit.")
    finish()
