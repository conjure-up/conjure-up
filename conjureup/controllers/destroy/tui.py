import sys

from conjureup import juju, utils
from conjureup.app_config import app


class Destroy:

    def render(self):
        utils.info("Destroying model {} in "
                   "controller {}".format(app.argv.model,
                                          app.argv.controller))
        try:
            juju.destroy_model(app.argv.controller, app.argv.model)
        except Exception as e:
            utils.error(
                "There was a problem destroying the model: {}".format(e))
            sys.exit(1)
        utils.info("Model has been removed")
        sys.exit(0)


_controller_class = Destroy
