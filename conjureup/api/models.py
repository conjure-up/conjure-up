""" Interfaces to Juju API ModelManager """

from conjureup import juju
from conjureup.app_config import app


@juju.requires_login
def list_models(user='user-admin'):
    """ Lists Juju Models

    Arguments:
    user: Name of user to list models for.

    Returns:
    Dictionary of known Juju Models (default: user-admin)
    """
    models = app.juju.client.ModelManager(request="ListModels",
                                          params={'Tag': user})
    return models['UserModels']


@juju.requires_login
def model_info(model):
    """ Returns information on select model

    Arguments:
    model: name of model to inspect

    Returns:
    Dictionary of model attributes
    """
    return app.juju.client.Client(request="ModelInfo",
                                  params={"Name": model})


@juju.requires_login
def model_status():
    """ Returns the FullStatus output of a model

    Returns:
    Dictionary of model status
    """
    return app.juju.client.Client(request="FullStatus")
