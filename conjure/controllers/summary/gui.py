from conjure.ui.views.deploy_summary import DeploySummaryView
from conjure.utils import pollinate
from conjure.app_config import app
from conjure import controllers


def finish(back=False, bundle=None):
    """ Does the actual deployment and loads the summary controller

    Arguments:
    back: If true will go back to previous controller
    """
    if back:
        return controllers.use('deploy').render(
            app.current_model
        )
    else:
        controllers.use('finish').render(bundle)


def render(bundle):
    excerpt = ("Please review the deployment summary before "
               "proceeding.")
    view = DeploySummaryView(app,
                             bundle,
                             finish)

    app.ui.set_header(
        title="Deploy Summary",
        excerpt=excerpt
    )
    app.ui.set_body(view)
    pollinate(app.session_id, 'SS')
