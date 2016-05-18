from conjure import controllers
from conjure import utils
from conjure.api.models import model_info
from conjure.app_config import app


def finish():
    """ handles deployment

    Arguments:
    back: if true returns to previous controller
    """
    utils.pollinate(app.session_id, 'PC')
    controllers.use('summary').render()


def render(model):
    app.current_model = model
    info = model_info(app.current_model)
    app.log.debug("Getting provider type: {}".format(info))

    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']
    finish()
