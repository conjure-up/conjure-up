from conjureup.ui.views.cloud import CloudView
from conjureup import async
from conjureup import utils
from conjureup import controllers
from conjureup.app_config import app
from conjureup import juju
import petname
from conjureup.controllers.clouds.common import (get_controller_in_cloud,
                                                 list_clouds)


class CloudsController:
    def __init__(self):
        self.view = None

    def __handle_exception(self, exc):
        utils.pollinate(app.session_id, "E004")
        app.ui.show_exception_message(exc)

    def __add_model(self):
        juju.switch_controller(app.current_controller)
        juju.add_model(app.current_model)
        juju.switch_model(app.current_model)

    def finish(self, cloud):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        cloud: Cloud to create the controller/model on.
        """
        utils.pollinate(app.session_id, 'CS')
        existing_controller = get_controller_in_cloud(cloud)

        if existing_controller is None:
            return controllers.use('newcloud').render(cloud)

        app.current_controller = existing_controller
        app.current_model = petname.Name()
        async.submit(self.__add_model,
                     self.__handle_exception,
                     queue_name=juju.JUJU_ASYNC_QUEUE)

        return controllers.use('bundlereadme').render()

    def render(self):
        clouds = list_clouds()
        excerpt = app.config.get(
            'description',
            "Please select from a list of available clouds")
        view = CloudView(app,
                         clouds,
                         self.finish)

        app.ui.set_header(
            title="Choose a Cloud",
            excerpt=excerpt
        )
        app.ui.set_body(view)


_controller_class = CloudsController
