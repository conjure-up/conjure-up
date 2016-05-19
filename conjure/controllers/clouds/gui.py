from conjure.ui.views.cloud import CloudView
from conjure import juju
from conjure import utils
from conjure import controllers
from conjure.app_config import app


def __list_clouds():
    """ Returns list of clouds filtering out any results
    """
    clouds = set(juju.get_clouds().keys())

    if 'cloud_whitelist' in app.config['metadata']:
        whitelist = set(app.config['metadata']['cloud_whitelist'])
        return sorted(list(clouds & whitelist))

    elif 'cloud_blacklist' in app.config['metadata']:
        blacklist = set(app.config['metadata']['cloud_blacklist'])
        return sorted(list(clouds ^ blacklist))

    return sorted(list(clouds))


def finish(cloud=None):
    """ Load the Model controller passing along the selected cloud.

    Arguments:
    cloud: Cloud to create the controller/model on.
    """
    utils.pollinate(app.session_id, 'CS')
    return controllers.use('newcloud').render(cloud)


def render():
    clouds = __list_clouds()
    excerpt = app.config['metadata'].get(
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
