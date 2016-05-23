from conjure.ui.views.variant import VariantView
from conjure import utils
from conjure import charm
from conjure import controllers
from conjure.app_config import app


def __get_bundles():
    """ Grabs a list of bundles matching our spell
    """
    # TODO: Remove false once bundles are promulgated
    res = charm.search(app.config['spell'], False)
    if res['Total'] > 0:
        return res['Results']


def finish(name):
    """ Finalizes welcome controller

    Arguments:
    name: name of charm/bundle to use
    """
    utils.pollinate(app.session_id, 'B001')
    return controllers.use('deploy').render(app.current_controller)


def render():
    view = VariantView(app, __get_bundles(), finish)
    app.log.debug("Rendering GUI controller for Variant")
    utils.pollinate(app.session_id, 'W001')
    app.ui.set_header(
        title='Spells'
    )
    app.ui.set_body(view)
