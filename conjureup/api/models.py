""" Interfaces to Juju API ModelManager """

import asyncio

from conjureup.app_config import app
from conjureup.juju import requires_login


@requires_login
def model_info():
    """ Returns information on the current model.

    Returns:
        ModelInfo object
    """
    return app.juju.client.info


@requires_login
def model_status():
    """ Returns the FullStatus output of a model

    Returns:
        FullStatus object
    """
    f = asyncio.run_coroutine_threadsafe(app.juju.client.get_status(),
                                         app.juju.client.loop)
    return f.result()
