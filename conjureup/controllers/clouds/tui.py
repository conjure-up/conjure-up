from conjureup import controllers, events, juju, utils
from conjureup.app_config import app


class CloudsController:

    def __controller_exists(self, controller):
        return juju.get_controller(controller) is not None

    def finish(self):
        if app.argv.model:
            app.provider.model = app.argv.model
        else:
            app.provider.model = utils.gen_model()

        return controllers.use('credentials').render()

    def render(self):
        utils.info(
            "Summoning {} to {}".format(app.argv.spell, app.provider.cloud))
        self.finish()


_controller_class = CloudsController
