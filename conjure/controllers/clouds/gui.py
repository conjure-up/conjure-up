from conjure.ui.views.cloud import CloudView
from conjure import juju
from conjure import utils
from conjure import controllers
from conjure.app_config import app


def __parse_whitelist():
    """ Parses all whitelists from multiple bundle results
    """
    current = []
    for bundle in app.bundles:
        try:
            for cloud \
                 in bundle['Meta']['extra-info/conjure']['cloud-whitelist']:
                if cloud not in current:
                    current.append(cloud)
        except:
            continue
    return current


def __parse_blacklist():
    """ Parses all blacklist from multiple bundle results
    """
    current = []
    for bundle in app.bundles:
        try:
            for cloud \
                 in bundle['Meta']['extra-info/conjure']['cloud-blacklist']:
                if cloud not in current:
                    current.append(cloud)
        except:
            continue
    return current


def __list_clouds():
    """ Returns list of clouds filtering out any results
    """
    clouds = set(juju.get_clouds().keys())

    if len(__parse_whitelist()) > 0:
        whitelist = set(__parse_whitelist())
        return sorted(list(clouds & whitelist))

    elif len(__parse_blacklist()) > 0:
        blacklist = set(__parse_blacklist())
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
