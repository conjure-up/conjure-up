""" Interfaces to Juju API ModelManager """

from conjure.juju import Juju, requires_login
import q


@q.t
@requires_login
def list_models(user='user-admin'):
    """ Lists Juju Models

    Arguments:
    user: Name of user to list models for.

    Returns:
    Dictionary of known Juju Models (default: user-admin)
    """
    models = Juju.client.ModelManager(request="ListModels",
                                      params={'Tag': user})
    return [x['Name'] for x in models['UserModels']]


@q.t
@requires_login
def model_info(model):
    """ Returns information on select model

    Arguments:
    model: name of model to inspect

    Returns:
    Dictionary of model attributes
    """
    return Juju.client.Client(request="ModelInfo",
                              params={"Name": model})
