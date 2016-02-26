""" Interfaces to Juju API ModelManager """

from conjure.juju import Juju, requires_login


@requires_login
def list_models():
    """ Lists Juju Models

    Arguments:
    user: Name of user to list models for.

    Returns:
    Dictionary of known Juju Models (default: user-admin)
    """
    models = Juju.client.ModelManager(request="ListModels",
                                      params={'Tag': 'user-admin'})
    return [x['Name'] for x in models['UserModels']]
