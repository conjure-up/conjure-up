from conjure import utils
from conjure.app_config import app


def finish(name):
    """ Finalizes welcome controller

    Arguments:
    name: name of charm/bundle to use
    """
    utils.pollinate(app.session_id, 'B001')


def render():
    pass
    # self.view = VariantView(self.app, self.finish)
    # self.app.log.debug("Rendering GUI controller for Variant")
    # pollinate(self.app.session_id, 'W001', self.app.log)
    # config = self.app.config
    # self.app.ui.set_header(
    #     title=config['summary'],
    #     excerpt=config['excerpt'],
    # )
    # self.app.ui.set_body(self.view)
