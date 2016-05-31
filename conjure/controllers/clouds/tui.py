from conjure import controllers
from conjure import juju
from conjure import utils
from conjure.app_config import app
from . import common
import petname
import sys
import os


def finish():
    if app.argv.cloud == "localhost":
        if not utils.check_bridge_exists():
            back = "{} to localhost".format(app.argv.config['spell'])
            os.execl("/usr/share/conjure-up/run-lxd-config",
                     "/usr/share/conjure-up/run-lxd-config",
                     back)

    have_existing_controller = common.controller_provides_ctype(app.argv.cloud)
    if have_existing_controller:
        utils.info("Creating environment, please wait.")
        app.current_controller = have_existing_controller
        juju.switch(have_existing_controller)
        app.current_model = petname.Name()
        juju.add_model(app.current_model)
        return controllers.use('variants').render()
    return controllers.use('newcloud').render(app.argv.cloud)


def render():
    if app.argv.cloud not in juju.get_clouds().keys():
        formatted_clouds = ", ".join(juju.get_clouds().keys())
        utils.warning("Unknown Cloud: {}, please choose "
                      "from one of the following: {}".format(app.argv.cloud,
                                                             formatted_clouds))
        sys.exit(1)
    utils.info(
        "Summoning {} to {}".format(app.argv.spell, app.argv.cloud))
    finish()
