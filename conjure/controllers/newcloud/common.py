import os.path as path
from conjure import utils
import yaml


def do_creds_exist(cloud):
    """ Check if credentials for existing cloud already exists so
    we can bypass the cloud config view and go straight to bootstrapping

    Arguments:
    cloud: public cloud
    """
    cred_path = path.join(utils.juju_path(), 'credentials.yaml')
    if not path.isfile(cred_path):
        return False

    existing_creds = yaml.safe_load(open(cred_path))
    if 'credentials' not in existing_creds:
        return False

    if cloud not in existing_creds['credentials'].keys():
        return False
    return True
