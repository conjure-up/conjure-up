from conjureup import juju
from conjureup.app_config import app


def parse_whitelist():
    """ Parses all whitelists from multiple bundle results
    """
    current = []
    if 'cloud-whitelist' in app.config['metadata']:
        for cloud in app.config['metadata']['cloud-whitelist']:
            if cloud not in current:
                current.append(cloud)
    return current


def parse_blacklist():
    """ Parses all blacklist from multiple bundle results
    """
    current = []
    if 'cloud-blacklist' in app.config['metadata']:
        for cloud in app.config['metadata']['cloud-blacklist']:
            if cloud not in current:
                current.append(cloud)

    return current


def list_clouds():
    """ Returns list of clouds filtering out any results
    """
    clouds = set(juju.get_clouds().keys())
    # Add support for maas here since juju doesn't display
    # this as a typical public cloud.
    clouds.add('maas')

    if len(parse_whitelist()) > 0:
        whitelist = set(parse_whitelist())
        return sorted(list(clouds & whitelist))

    elif len(parse_blacklist()) > 0:
        blacklist = set(parse_blacklist())
        return sorted(list(clouds ^ blacklist))

    return sorted(list(clouds))


def get_controller_in_cloud(cloud):
    """ Returns a controller that is bootstrapped on the named cloud

    Arguments:
    cloud: cloud to check for

    Returns:
    available controller or None if nothing available
    """
    controllers = juju.get_controllers()['controllers'].items()
    for controller_name, controller in controllers:
        if cloud == controller['cloud']:
            return controller_name
    return None
