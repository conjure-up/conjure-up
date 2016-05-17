from conjure.ui.views.newcloud import NewCloudView
from conjure.models.provider import Schema
from conjure import utils
from conjure import controllers
from conjure.app_config import app
import os.path as path
import yaml
import petname
import sys

from .common import check_bridge_exists

this = sys.modules[__name__]
this.cloud = None


def __format_creds(creds):
    """ Formats the credentials into strings from the widgets values
    """
    formatted = {}
    for k, v in creds.items():
        if k.startswith('_'):
            # Not a widget but a private key
            k = k[1:]
            formatted[k] = v
        elif k.startswith('@'):
            # A Widget, but not stored in credentials
            continue
        else:
            formatted[k] = v.value
    return formatted


def finish(credentials=None, back=False):
    """ Load the Model controller passing along the selected cloud.

    Arguments:
    credentials: credentials to store for provider
    back: if true loads previous controller
    """
    app.current_controller = petname.Name()

    if back:
        return controllers.use('welcome').render()

    cred_path = path.join(utils.juju_path(), 'credentials.yaml')
    if not path.isfile(cred_path):
        existing_creds = {
                'credentials': {
                    this.cloud: {
                        app.current_controller: __format_creds(
                            credentials)
                    }
                }
            }

    else:
        existing_creds = yaml.safe_load(open(cred_path))

        if this.cloud in existing_creds['credentials'].keys():
            c = existing_creds['credentials'][this.cloud]
            c[app.current_controller] = __format_creds(
                credentials)
        else:
            # Handle the case where path exists but an entry for the cloud
            # has yet to be added.
            existing_creds['credentials'][this.cloud] = {
                app.current_controller: __format_creds(
                    credentials)
            }

    with open(cred_path, 'w') as cred_f:
        cred_f.write(yaml.safe_dump(existing_creds,
                                    default_flow_style=False))

    if this.cloud == 'maas':
        this.cloud = '{}/{}'.format(this.cloud,
                                    credentials['@maas-server'].value)
    utils.pollinate(app.session_id, 'CA')
    controllers.use('jujucontroller').render(
        this.cloud, bootstrap=True)


def render(cloud):
    """ Render

    Arguments:
    cloud: The cloud to create credentials for
    """

    # LXD is a special case as we want to make sure a bridge
    # is configured. If not we'll bring up a new view to allow
    # a user to configure a LXD bridge with suggested network
    # information.
    if cloud == 'localhost':
        if not check_bridge_exists():
            return controllers.use('lxdsetup').render()

        app.log.debug("Found an IPv4 address, "
                      "assuming LXD is configured.")
        return controllers.use('jujucontroller').render(
            cloud='localhost', bootstrap=True)

    try:
        creds = Schema[cloud]
    except KeyError as e:
        utils.pollinate(app.session_id, 'EC')
        return app.ui.show_exception_message(e)

    this.cloud = cloud
    view = NewCloudView(app,
                        this.cloud,
                        creds,
                        finish)

    app.ui.set_header(
        title="New cloud setup",
    )
    app.ui.set_body(view)
