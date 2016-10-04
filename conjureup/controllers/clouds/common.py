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

    if len(parse_whitelist()) > 0:
        whitelist = set(parse_whitelist())
        return sorted(list(clouds & whitelist))

    elif len(parse_blacklist()) > 0:
        blacklist = set(parse_blacklist())
        return sorted(list(clouds ^ blacklist))

    return sorted(list(clouds))
