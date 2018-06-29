""" MAAS module for configuring endpoint
"""

from conjureup import errors, juju
from conjureup.app_config import app


def setup_maas():
    maascreds = juju.get_credential(app.provider.cloud,
                                    app.provider.credential)
    if not maascreds:
        raise errors.MAASConfigError(
            "Could not find MAAS credentials for cloud: {}".format(
                app.provider.cloud))
    try:
        endpoint = juju.get_cloud(app.provider.cloud).get('endpoint', None)
        app.log.debug(
            "Found endpoint: {} for cloud: {}".format(
                endpoint,
                app.provider.cloud))
    except LookupError:
        app.log.debug("Failed to find cloud in list-clouds, "
                      "attempting to read bootstrap-config")
        bc = juju.get_bootstrap_config(app.provider.controller)
        endpoint = bc.get('endpoint', None)

    if endpoint is None:
        raise errors.MAASConfigError("Couldn't find endpoint for controller: "
                                     "{}".format(app.provider.controller))

    try:
        api_key = maascreds['maas-oauth']
        consumer_key, token_key, token_secret = api_key.split(':')
    except (KeyError, ValueError):
        raise errors.MAASConfigError("Could not parse MAAS API Key")

    app.maas.endpoint = endpoint
    app.maas.api_key = api_key
