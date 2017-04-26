from conjureup import controllers, juju, utils
from conjureup.app_config import app
from conjureup.models.provider import load_schema
from conjureup.telemetry import track_exception, track_screen
from conjureup.ui.views.newcloud import NewCloudView

from . import common


class NewCloudController:
    def render(self):
        track_screen("Cloud Creation")

        if app.current_controller is None:
            app.current_controller = "conjure-up-{}-{}".format(
                app.current_cloud,
                utils.gen_hash())

        if app.current_model is None:
            app.current_model = utils.gen_model()

        cloud_type = juju.get_cloud_types_by_name()[app.current_cloud]

        # LXD is a special case as we want to make sure a bridge
        # is configured. If not we'll bring up a new view to allow
        # a user to configure a LXD bridge with suggested network
        # information.
        if cloud_type == 'localhost':
            lxd = common.is_lxd_ready()
            if not lxd['ready']:
                return controllers.use('lxdsetup').render(lxd['msg'])
            # lxd doesn't require user-provided credentials,
            # so never show the editor for localhost
            return self.finish()

        creds = common.try_get_creds(app.current_cloud)
        try:
            endpoint = juju.get_cloud(app.current_cloud).get('endpoint', None)
        except LookupError:
            endpoint = None
        if creds and (endpoint or cloud_type != 'maas'):
            return self.finish()

        # show credentials editor otherwise
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

        view = NewCloudView(creds, self.finish)

        app.ui.set_header(
            title="New cloud setup",
        )
        app.ui.set_body(view)
        app.ui.set_footer("")

    def finish(self, credentials=None, back=False):
        if back:
            return controllers.use('clouds').render()

        region = None
        if credentials is not None:
            cloud_type = juju.get_cloud_types_by_name()[app.current_cloud]
            if cloud_type == 'maas':
                # Now that we are passed the selection of a cloud we create a
                # new cloud name for the remainder of the deployment and make
                # sure this cloud is saved for future use.
                app.current_cloud = utils.gen_cloud()

                # Save credentials for new cloud
                common.save_creds(app.current_cloud, credentials)

                try:
                    juju.get_cloud(app.current_cloud)
                except LookupError:
                    juju.add_cloud(app.current_cloud,
                                   credentials.cloud_config(
                                       credentials.endpoint.value))
            else:
                common.save_creds(app.current_cloud, credentials)
        credentials_key = common.try_get_creds(app.current_cloud)
        app.loop.create_task(common.do_bootstrap(credentials_key,
                                                 region=region,
                                                 msg_cb=app.ui.set_footer,
                                                 fail_msg_cb=lambda e: None))
        controllers.use('deploy').render()


_controller_class = NewCloudController
