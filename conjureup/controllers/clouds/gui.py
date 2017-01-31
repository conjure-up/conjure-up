from conjureup import controllers
from conjureup.app_config import app
from conjureup.controllers.clouds.common import list_clouds
from conjureup.telemetry import track_event, track_screen
from conjureup.ui.views.cloud import CloudView


class CloudsController:

    def __init__(self):
        self.view = None

    def finish(self, cloud):
        """Show the 'newcloud' screen to enter credentials for a new
        controller on 'cloud'.  There will not be an existing
        controller.

        Arguments:
        cloud: Cloud to create the controller/model on.

        """
        app.current_cloud = cloud
        track_event("Cloud selection", app.current_cloud, "")
        return controllers.use('newcloud').render()

    def render(self):
        "Pick or create a cloud to bootstrap a new controller on"
        track_screen("Cloud Select")
        clouds = list_clouds()
        excerpt = app.config.get(
            'description',
            "Please select from a list of available clouds")
        view = CloudView(app,
                         clouds,
                         cb=self.finish)

        app.ui.set_header(
            title="Choose a Cloud",
            excerpt=excerpt
        )
        app.ui.set_body(view)
        app.ui.set_footer('Please press [ENTER] on highlighted '
                          'Cloud to proceed.')


_controller_class = CloudsController
