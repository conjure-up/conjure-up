import sys

from conjureup import controllers, juju, utils
from conjureup.app_config import app


class CloudsController:

    def __get_existing_controller(self, controller):
        if juju.get_controller(controller):
            return juju.get_controller_in_cloud(app.argv.cloud)
        return None

    def finish(self):
        if app.argv.model:
            app.current_model = app.argv.model
        else:
            app.current_model = "conjure-up-{}-{}".format(
                app.env['CONJURE_UP_SPELL'],
                utils.gen_hash())

        if not app.argv.controller:
            app.current_controller = "conjure-up-{}-{}".format(
                app.current_cloud,
                utils.gen_hash())

            return controllers.use('newcloud').render()

        app.current_controller = app.argv.controller
        if self.__get_existing_controller(app.current_controller) is None:
            return controllers.use('newcloud').render()
        else:
            utils.info("Using controller '{}'".format(app.current_controller))
            utils.info("Creating new model named '{}', "
                       "please wait.".format(app.current_model))
            juju.add_model(app.current_model, app.current_controller)
            return controllers.use('deploy').render()

        utils.error("Something happened with the controller or model, "
                    "please check the logs.")
        sys.exit(1)

    def render(self):
        if app.current_cloud not in juju.get_clouds().keys():
            formatted_clouds = ", ".join(juju.get_clouds().keys())
            utils.warning(
                "Unknown Cloud: {}, please choose "
                "from one of the following: {}".format(app.current_cloud,
                                                       formatted_clouds))
            sys.exit(1)
        utils.info(
            "Summoning {} to {}".format(app.argv.spell, app.argv.cloud))
        self.finish()


_controller_class = CloudsController
