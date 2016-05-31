from conjure.ui.views.cloud import CloudView
from conjure import utils
from conjure import controllers
from conjure.app_config import app
from conjure import juju
import petname
from . import common


def finish(cloud):
    """ Load the Model controller passing along the selected cloud.

    Arguments:
    cloud: Cloud to create the controller/model on.
    """
    utils.pollinate(app.session_id, 'CS')
    have_existing_controller = common.controller_provides_ctype(cloud)
    if have_existing_controller:
        app.current_controller = have_existing_controller
        juju.switch(have_existing_controller)
        # If a cloud exists create a new model for current deployment
        app.current_model = petname.Name()
        juju.add_model(app.current_model)
        return controllers.use('variants').render()
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
