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


def model_cache_environment(controller):
    """ Returns known controller environment defined in the models
    cache.

    Arguments:
    controller: name of controller environment
    """
    return Juju.model_cache()['environments'].get(controller, False)


def model_cache_server_data(uuid):
    """ Returns server data for controller

    Arguments:
    uuid: server uuid for controller environment
    """
    return Juju.model_cache()['server-data'].get(uuid, False)


def model_cache_controller_provider(uuid):
    """ Returns provider information for controller

    Arguments:
    uuid: server uuid for controller environment

    Returns:
    config or false.
    """
    s = model_cache_server_data(uuid)
    if s:
        return s['bootstrap-config']
    return False
