from conjureup import controllers, events, juju, utils
from conjureup.app_config import app


class CloudsController:

    def __controller_exists(self, controller):
        return juju.get_controller(controller) is not None

    def finish(self):
        if app.argv.model:
            app.current_model = app.argv.model
        else:
            app.current_model = utils.gen_model()

        if not app.argv.controller:
            app.current_controller = "conjure-up-{}-{}".format(
                app.current_cloud,
                utils.gen_hash())

            return controllers.use('regions').render()

        app.current_controller = app.argv.controller
        if not self.__controller_exists(app.current_controller):
            return controllers.use('regions').render()
        else:
            utils.info("Using controller '{}'".format(app.current_controller))
            utils.info("Creating new model named '{}', "
                       "please wait.".format(app.current_model))
            app.loop.create_task(juju.add_model(app.current_model,
                                                app.current_controller,
                                                app.current_cloud,
                                                allow_exists=True))
            return controllers.use('deploy').render()

        utils.error("Something happened with the controller or model, "
                    "please check the logs.")
        events.Shutdown.set(1)

    def render(self):
        if app.current_cloud not in juju.get_clouds().keys():
            formatted_clouds = ", ".join(juju.get_clouds().keys())
            utils.error(
                "Unknown Cloud: {}, please choose "
                "from one of the following: {}".format(app.current_cloud,
                                                       formatted_clouds))
            events.Shutdown.set(1)
            return
        utils.info(
            "Summoning {} to {}".format(app.argv.spell, app.argv.cloud))
        self.finish()


_controller_class = CloudsController
