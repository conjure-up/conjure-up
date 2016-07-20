from conjure import utils
from conjure import controllers
from conjure.app_config import app


class VariantsController:
    def finish(self):
        """ Finalizes welcome controller

        Arguments:
        name: name of charm/bundle to use
        """
        utils.pollinate(app.session_id, 'B001')
        return controllers.use('deploy').render()

    def render(self):
        self.finish()


_controller_class = VariantsController
