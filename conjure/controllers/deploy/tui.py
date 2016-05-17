from conjure.api.models import model_info
from conjure import utils
from conjure.app_config import app
from conjure import controllers


def finish():
    """ handles deployment

    Arguments:
    back: if true returns to previous controller
    """
    utils.pollinate(app.session_id, 'PC')
    controllers.use('deploysummary').render()


def render(model):
    app.current_model = model
    info = model_info(app.current_model)

    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']
    finish()
