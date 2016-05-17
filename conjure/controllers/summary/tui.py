from conjure import utils
from conjure.app_config import app
from conjure import controllers


def finish(bundle=None):
    """ hands off to deploy

    Arguments:
    bundle: bundle path
    """
    controllers.use('finish').render(bundle)


def render(bundle):
    utils.pollinate(app.session_id, 'SS')
    finish(bundle)
