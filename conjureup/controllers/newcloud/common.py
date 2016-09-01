import os.path as path

import yaml

from conjureup import utils
from conjureup.app_config import app

cred_path = path.join(utils.juju_path(), 'credentials.yaml')


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


def try_get_creds(cloud):
    """ Check if credentials for existing cloud already exists so
    we can bypass the cloud config view and go straight to bootstrapping

    Arguments:
    cloud: public cloud

    Returns:
    First set of credentials found for cloud
    """
    if not path.isfile(cred_path):
        return None

    existing_creds = yaml.safe_load(open(cred_path))
    if 'credentials' not in existing_creds:
        return None

    if cloud not in existing_creds['credentials'].keys():
        return None

    if len(existing_creds['credentials'][cloud].keys()) == 0:
        return None

    first_cred = list(existing_creds['credentials'][cloud].keys())[0]
    return first_cred


def save_creds(cloud, credentials):
    """ stores credentials for cloud
    """
    try:
        existing_creds = yaml.safe_load(open(cred_path))
    except:
        existing_creds = {'credentials': {}}

    if cloud in existing_creds['credentials'].keys():
        c = existing_creds['credentials'][cloud]
        c[app.current_controller] = __format_creds(
            credentials)
    else:
        # Handle the case where path exists but an entry for the cloud
        # has yet to be added.
        existing_creds['credentials'][cloud] = {
            app.current_controller: __format_creds(
                credentials)
        }

    with open(cred_path, 'w') as cred_f:
        cred_f.write(yaml.safe_dump(existing_creds,
                                    default_flow_style=False))
