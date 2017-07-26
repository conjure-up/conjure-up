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

        return controllers.use('credentials').render()

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
