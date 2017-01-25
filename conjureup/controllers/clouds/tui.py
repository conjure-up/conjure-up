import sys

from conjureup import controllers, juju, utils
from conjureup.app_config import app


class CloudsController:

    def finish(self):
        if app.argv.controller:
            existing_controller = app.argv.controller
            if juju.get_controller(existing_controller) is None:
                utils.error("Specified controller '{}' "
                            "could not be found in cloud '{}'.".format(
                                existing_controller, app.argv.cloud))
                sys.exit(1)
        else:
            existing_controller = juju.get_controller_in_cloud(app.argv.cloud)

        if existing_controller is None:
            app.current_cloud = app.argv.cloud
            return controllers.use('newcloud').render()

        utils.info("Using controller '{}'".format(existing_controller))

        app.current_controller = existing_controller
        app.current_model = "conjure-up-{}-{}".format(
            app.env['CONJURE_UP_SPELL'],
            utils.gen_hash())
        utils.info("Creating new juju model named '{}', "
                   "please wait.".format(app.current_model))
        juju.add_model(app.current_model, app.current_controller)

        return controllers.use('deploy').render()

    def render(self):
        if app.argv.cloud not in juju.get_clouds().keys():
            formatted_clouds = ", ".join(juju.get_clouds().keys())
            utils.warning(
                "Unknown Cloud: {}, please choose "
                "from one of the following: {}".format(app.argv.cloud,
                                                       formatted_clouds))
            sys.exit(1)
        utils.info(
            "Summoning {} to {}".format(app.argv.spell, app.argv.cloud))
        self.finish()


_controller_class = CloudsController
