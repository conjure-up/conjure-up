from conjureup import controllers, juju, utils
from conjureup.app_config import app
from conjureup.telemetry import track_event, track_screen
from conjureup.ui.views.cloud import CloudView


class CloudsController:

    def __init__(self):
        self.view = None

    def finish(self, cloud):
        """Save the selected cloud and move on to the region selection screen.

        """
        if cloud == 'maas':
            app.current_cloud_type = 'maas'
            app.current_cloud = utils.gen_cloud()
        else:
            app.current_cloud_type = juju.get_cloud_types_by_name()[cloud]
            app.current_cloud = cloud

        if app.current_controller is None:
            app.current_controller = "conjure-up-{}-{}".format(
                app.current_cloud,
                utils.gen_hash())

        if app.current_model is None:
            app.current_model = utils.gen_model()

        track_event("Cloud selection", app.current_cloud, "")
        return controllers.use('regions').render()

    def render(self):
        "Pick or create a cloud to bootstrap a new controller on"
        track_screen("Cloud Select")

        compatible_clouds = juju.get_compatible_clouds()
        all_clouds = juju.get_clouds()
        clouds = []

        for k, v in all_clouds.items():
            if v['type'] in compatible_clouds:
                clouds.append(k)

        excerpt = app.config.get(
            'description',
            "Please select from a list of available clouds")
        view = CloudView(app,
                         sorted(clouds),
                         cb=self.finish)

        app.ui.set_header(
            title="Choose a Cloud",
            excerpt=excerpt
        )
        app.ui.set_body(view)
        app.ui.set_footer('Please press [ENTER] on highlighted '
                          'Cloud to proceed.')


_controller_class = CloudsController
