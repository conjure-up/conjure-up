from conjure import controllers
from conjure import utils

from conjure.app_config import app


def finish():
    """ handles deployment

    Arguments:
    back: if true returns to previous controller
    """
    utils.pollinate(app.session_id, 'PC')
    controllers.use('finish').render()


def render():
    finish()
