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
            common.save_creds(app.current_cloud, credentials)
            cloud_type = juju.get_cloud_types_by_name()[app.current_cloud]
            if cloud_type == 'maas':
                # when bootstrapping a MAAS controller that hasn't been added
                # as a saved cloud, we have to provide the API endpoint as
                # the "region" when bootstrapping
                region = credentials.fields()[0].value

            # XXX: Oracle is handled special case until that cloud is
            # solidified and makes it into Juju's default cloud listing
            if cloud_type == 'oracle':
                # need to create a custom cloud here with endpoint for oracle
                endpoint = credentials.fields()[3].value
                oracle_config = {
                    'type': 'oracle',
                            'description': 'Oracle Cloud',
                            'auth-types': ['userpass'],
                            'endpoint': endpoint,
                            'regions': {
                                'uscom-central-1': {}
                            }
                }
                try:
                    juju.get_cloud('oracle')
                except LookupError:
                    juju.add_cloud('oracle', oracle_config)

        credentials_key = common.try_get_creds(app.current_cloud)
        app.loop.create_task(common.do_bootstrap(credentials_key,
                                                 region=region,
                                                 msg_cb=app.ui.set_footer,
                                                 fail_msg_cb=lambda e: None))
        controllers.use('deploy').render()


_controller_class = NewCloudController
