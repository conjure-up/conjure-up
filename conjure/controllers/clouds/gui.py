from conjure.ui.views.cloud import CloudView
from conjure import utils
from conjure import controllers
from conjure.app_config import app
from . import common


def finish(cloud=None):
    """ Load the Model controller passing along the selected cloud.

    Arguments:
    cloud: Cloud to create the controller/model on.
    """
    utils.pollinate(app.session_id, 'CS')
    return controllers.use('newcloud').render(cloud)


def render():
    clouds = common.list_clouds()
    excerpt = app.config.get(
        'description',
        "Please select from a list of available clouds")
    view = CloudView(app,
                     clouds,
                     finish)

    app.ui.set_header(
        title="Choose a Public Cloud",
        excerpt=excerpt
    )
    app.ui.set_body(view)
