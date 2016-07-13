from conjure.ui.views.bootstrapwait import BootstrapWaitView
from conjure.app_config import app
from conjure import controllers


def finish(deploy_future=None):
    return controllers.use('deploystatus').render(deploy_future)


def render(deploy_future=None):
    app.log.debug("Rendering bootstrap wait")

    view = BootstrapWaitView(app)
    app.ui.set_header(title="Waiting for Bootstrap")
    app.ui.set_body(view)
    # finish()
