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

        if app.current_model is None:
            app.current_model = utils.gen_model()

        track_event("Cloud selection", app.current_cloud, "")
        return controllers.use('regions').render()

    def render(self):
        "Pick or create a cloud to bootstrap a new controller on"
        track_screen("Cloud Select")

        all_clouds = juju.get_clouds()
        compatible_clouds = juju.get_compatible_clouds()
        cloud_types = juju.get_cloud_types_by_name()
        # filter to only public clouds
        public_clouds = sorted(
            name for name, info in all_clouds.items()
            if info['defined'] == 'public' and
            cloud_types[name] in compatible_clouds)
        # filter to custom clouds
        # exclude localhost because we treat that as "configuring a new cloud"
        custom_clouds = sorted(
            name for name, info in all_clouds.items()
            if info['defined'] != 'public' and
            cloud_types[name] != 'localhost' and
            cloud_types[name] in compatible_clouds)

        excerpt = app.config.get(
            'description',
            "Where would you like to deploy?")
        view = CloudView(app,
                         public_clouds,
                         custom_clouds,
                         cb=self.finish)

        app.ui.set_header(
            title="Choose a Cloud",
            excerpt=excerpt
        )
        app.ui.set_body(view)
        app.ui.set_footer('Please press [ENTER] on highlighted '
                          'Cloud to proceed.')


_controller_class = CloudsController
