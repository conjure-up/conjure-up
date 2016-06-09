from conjure import juju
from conjure.app_config import app


def parse_whitelist():
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


def parse_blacklist():
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


def controller_provides_ctype(cloud):
    """ Returns a controller that is bootstrapped and fulfills
    the cloud type.

    Arguments:
    cloud: cloud to check for

    Returns:
    available controller or None if nothing available
    """
    if not juju.available():
        return None
    if cloud == 'maas':
        cloud_type = 'maas'
    else:
        cloud_type = juju.get_cloud(cloud)['type']
    for c in juju.get_controllers()['controllers'].keys():
        juju.switch(c)
        loaded_cloud_type = juju.get_model(juju.get_current_model())['type']
        if cloud_type == loaded_cloud_type:
            return c
    return None
