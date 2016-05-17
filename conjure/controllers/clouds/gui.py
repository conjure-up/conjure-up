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


def finish(cloud=None, create_cloud=False):
    """ Load the Model controller passing along the selected cloud.

    Arguments:
    cloud: Cloud to create the controller/model on.
    create_cloud: True/False, if true display create cloud interface
    """
    if create_cloud:
        return controllers.use('newcloud').render(cloud)

    utils.pollinate(app.session_id, 'CS')


def render():
    clouds = __list_clouds()
    excerpt = ("Please select from a list of available clouds")
    view = CloudView(app,
                     clouds,
                     finish)

    app.ui.set_header(
        title="Cloud Providers",
        excerpt=excerpt
    )
    app.ui.set_body(view)
