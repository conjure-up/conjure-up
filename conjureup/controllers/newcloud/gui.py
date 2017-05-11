from conjureup import controllers, juju, utils
from conjureup.app_config import app
from conjureup.models.provider import load_schema
from conjureup.telemetry import track_exception, track_screen
from conjureup.ui.views.newcloud import NewCloudView

from . import common


class NewCloudController:
    def render_newcloud(self):
        """ Renders new cloud provider form
        """
        try:
            creds = load_schema(app.current_cloud)
        except Exception as e:
            track_exception("Credentials Error: {}".format(e))
            app.log.exception("Credentials Error: {}".format(e))
            return app.ui.show_exception_message(
                Exception(
                    "Unable to find credentials for {}, "
                    "you can double check what credentials you "
                    "do have available by running "
                    "`juju credentials`. Please see `juju help "
                    "add-credential` for more information.".format(
                        app.current_cloud)))

        regions = []
        # No regions for these providers
        if self.cloud_type not in ['maas', 'vsphere', 'localhost']:
            regions = sorted(juju.get_regions(app.current_cloud).keys())

        view = NewCloudView(creds, regions, self.finish)

        app.ui.set_header(
            title="New cloud setup",
        )
        app.ui.set_body(view)
        app.ui.set_footer("")

    def render(self):
        track_screen("Cloud Creation")
        self.cloud_type = juju.get_cloud_types_by_name()[app.current_cloud]

        if app.current_controller is None:
            app.current_controller = "conjure-up-{}-{}".format(
                app.current_cloud,
                utils.gen_hash())

        if app.current_model is None:
            app.current_model = utils.gen_model()

        # LXD is a special case as we want to make sure a bridge
        # is configured. If not we'll bring up a new view to allow
        # a user to configure a LXD bridge with suggested network
        # information.
        if self.cloud_type == 'localhost':
            lxd_setup_path = common.get_lxd_setup_path()
            app.log.debug("Determining if embedded LXD is setup and ready.")
            if lxd_setup_path.exists():
                return self.finish()
            else:
                self.render_newcloud()

        # TODO: Prompt user to select credentials and set a region
        creds = common.try_get_creds(app.current_cloud)
        try:
            endpoint = juju.get_cloud(app.current_cloud).get(
                'endpoint', None)
        except LookupError:
            endpoint = None
        if creds and (endpoint or self.cloud_type != 'maas'):
            return self.finish()

        # No existing credentials found, start credential editor
        self.render_newcloud()

    def finish(self, schema=None, region=None, back=False):
        if region:
            app.current_region = region

        if back:
            return controllers.use('clouds').render()

        if schema is not None:
            # Attempt to setup LXD with our selected interface
            if self.cloud_type == 'localhost':
                try:
                    common.lxd_init(schema.network_interface.value)

                    # Store LXD setup completion so we dont reconfigure on
                    # subsequent runs
                    common.get_lxd_setup_path().touch()
                except Exception:
                    raise

            if self.cloud_type == 'maas':
                # Now that we are passed the selection of a cloud we create a
                # new cloud name for the remainder of the deployment and make
                # sure this cloud is saved for future use.
                app.current_cloud = utils.gen_cloud()

                # Save credentials for new cloud
                common.save_creds(app.current_cloud, schema)

                try:
                    juju.get_cloud(app.current_cloud)
                except LookupError:
                    juju.add_cloud(app.current_cloud,
                                   schema.cloud_config())
            else:
                common.save_creds(app.current_cloud, schema)
        credentials_key = common.try_get_creds(app.current_cloud)
        app.loop.create_task(common.do_bootstrap(credentials_key,
                                                 msg_cb=app.ui.set_footer,
                                                 fail_msg_cb=lambda e: None))
        controllers.use('deploy').render()


_controller_class = NewCloudController
