from conjure import juju
from conjure import utils
from conjure import controllers
from conjure.app_config import app
import sys


def finish():
    controllers.use('jujucontroller').render(app.argv.cloud)


def render():
    if app.argv.cloud not in juju.get_clouds().keys():
        utils.warning("Unknown Cloud: {}".format(app.argv.cloud))
        sys.exit(1)
    utils.info(
        "Summoning {} to {}.".format(app.argv.spell, app.argv.cloud))
    finish()
