import json
import os
import os.path as path
from functools import partial
from subprocess import check_output

from conjureup import async, controllers, juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app
from conjureup.models.provider import load_schema
from conjureup.telemetry import track_event, track_exception, track_screen
from conjureup.ui.views.newcloud import NewCloudView

from . import common


class NewCloudController:

    def __handle_exception(self, exc):
        if app.showing_error:
            return
        app.showing_error = True
        track_exception(exc.args[0])
        app.ui.show_exception_message(exc)

    def __handle_bootstrap_done(self, future):
        app.log.debug("handle bootstrap")
        if future.exception():
            return
        result = future.result()
        if result.returncode < 0:
            self.__handle_exception(
                Exception("Bootstrap killed by user: {}".format(
                    result.returncode)))
            return
        if result.returncode > 0:
            pathbase = os.path.join(
                app.config['spell-dir'],
                '{}-bootstrap').format(app.current_controller)

            with open(pathbase + ".err") as errf:
                err = "\n".join(errf.readlines())
                app.log.error(err)
            e = Exception("Bootstrap error: {}".format(err))
            self.__handle_exception(e)
            return

        track_event("Juju Bootstrap", "Done", "")
        app.ui.set_footer('Bootstrap complete...')
        self.__post_bootstrap_exec()

    def __do_bootstrap(self, credential=None, cloud_with_creds=None):
        if cloud_with_creds:
            cloud = cloud_with_creds
        else:
            cloud = app.current_cloud

        app.log.debug("Performing bootstrap: {} {}".format(
            app.current_controller, cloud))

        app.ui.set_footer('Bootstrapping Juju controller in the background...')

        future = juju.bootstrap_async(
            controller=app.current_controller,
            cloud=cloud,
            model=app.current_model,
            credential=credential,
            exc_cb=self.__handle_exception)
        app.bootstrap.running = future
        if future is None:
            return
        future.add_done_callback(self.__handle_bootstrap_done)
        controllers.use('deploy').render()

    def __post_bootstrap_exec(self):
        """ Executes post-bootstrap.sh if exists
        """
        info = model_info(app.current_model)
        # Set our provider type environment var so that it is
        # exposed in future processing tasks
        app.env['JUJU_PROVIDERTYPE'] = info['provider-type']
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model
        _post_bootstrap_sh = path.join(app.config['spell-dir'],
                                       'steps/00_post-bootstrap')
        app.log.debug(
            'Checking for post bootstrap task: {}'.format(_post_bootstrap_sh))
        if path.isfile(_post_bootstrap_sh) \
           and os.access(_post_bootstrap_sh, os.X_OK):
            app.ui.set_footer('Running post-bootstrap tasks...')
            track_event("Juju Post-Bootstrap", "Started", "")
            app.log.debug("post_bootstrap running: {}".format(
                _post_bootstrap_sh
            ))
            try:
                future = async.submit(partial(check_output,
                                              _post_bootstrap_sh,
                                              shell=True,
                                              env=app.env),
                                      self.__handle_exception)
                if future:
                    future.add_done_callback(self.__post_bootstrap_done)
            except Exception as e:
                return self.__handle_exception(e)

    def __post_bootstrap_done(self, future):
        try:
            result = json.loads(future.result().decode('utf8'))
        except Exception as e:
            return self.__handle_exception(e)

        app.log.debug("post_bootstrap_done: {}".format(result))
        if result['returnCode'] > 0:
            track_exception("Error in Post-Bootstrap")
            return self.__handle_exception(Exception(
                'There was an error during the post '
                'bootstrap processing phase: {}.'.format(result)))
        track_event("Juju Post-Bootstrap", "Done", "")
        app.ui.set_footer('')

    def finish(self, credentials=None, back=False):
        """ Load the Model controller passing along the selected cloud.

        Arguments:
        credentials: credentials to store for provider
        back: if true loads previous controller
        """
        if back:
            return controllers.use('clouds').render()

        if credentials is not None:
            common.save_creds(app.current_cloud, credentials)
        credentials_key = common.try_get_creds(app.current_cloud)

        cloud_with_creds = None
        if app.current_cloud == 'maas':
            cloud_with_creds = '{}/{}'.format(
                app.current_cloud, credentials['fields'][0]['input'].value)
        self.__do_bootstrap(credential=credentials_key,
                            cloud_with_creds=cloud_with_creds)

    def render(self):
        track_screen("Cloud Creation")

        if app.current_controller is None:
            app.current_controller = "conjure-up-{}-{}".format(
                app.current_cloud,
                utils.gen_hash())

        if app.current_model is None:
            app.current_model = "conjure-up-{}-{}".format(
                app.env['CONJURE_UP_SPELL'],
                utils.gen_hash())

        # LXD is a special case as we want to make sure a bridge
        # is configured. If not we'll bring up a new view to allow
        # a user to configure a LXD bridge with suggested network
        # information.

        try:
            cloud = juju.get_cloud(app.current_cloud)

            if cloud['type'] == 'lxd':
                common.is_lxd_ready()
                self.__do_bootstrap()
                return
        except LookupError as e:
            # TODO: Add vsphere once lp bug 1671650 is resolved
            if app.current_cloud in ['maas']:
                app.log.debug(
                    "Not a cloud, using provider type: {}".format(
                        app.current_cloud))
            else:
                raise Exception(e)

        # XXX: always prompt for maas information for now as there is no way to
        # logically store the maas server ip for future sessions.
        if common.try_get_creds(app.current_cloud) \
           is not None and app.current_cloud != 'maas':
            self.__do_bootstrap(
                credential=common.try_get_creds(app.current_cloud))
            return controllers.use('deploy').render()

        # show credentials editor otherwise
        try:
            creds = load_schema(app.current_cloud)
        except Exception as e:
            track_exception("Credentials Error: {}".format(e))
            return app.ui.show_exception_message(
                Exception(
                    "Unable to find credentials for cloud "
                    "looking for {}".format(app.current_cloud)))

        view = NewCloudView(creds, self.finish)

        app.ui.set_header(
            title="New cloud setup",
        )
        app.ui.set_body(view)
        app.ui.set_footer("")


_controller_class = NewCloudController
