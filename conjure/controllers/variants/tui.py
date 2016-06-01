from conjure import utils
from conjure import controllers
from conjure.app_config import app


def finish():
    """ Finalizes welcome controller

    Arguments:
    name: name of charm/bundle to use
    """
    utils.pollinate(app.session_id, 'B001')
    return controllers.use('deploy').render()


def render():
    finish()
