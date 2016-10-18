import json
import os
import os.path as path
from functools import partial
from subprocess import check_output

import petname

from conjureup import async, controllers, juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app
from conjureup.maas import MaasClient
from conjureup.models.provider import Schema
from conjureup.telemetry import track_event, track_exception, track_screen
from conjureup.ui.views.newcloud import NewCloudView
from ubuntui.ev import EventLoop

from . import common


class NewCloudController:

    def __init__(self):
        self.cloud = None

    def __handle_exception(self, exc):
        track_exception(exc.args[0])
        return app.ui.show_exception_message(exc)

    def __handle_bootstrap_done(self, future):
        app.log.debug("handle bootstrap")
        result = future.result()
        if result.returncode < 0:
            # bootstrap killed via user signal, we're quitting
            return
        if result.returncode > 0:
            pathbase = os.path.join(
                app.config['spell-dir'],
                '{}-bootstrap').format(app.current_controller)

            with open(pathbase + ".err") as errf:
                err = "\n".join(errf.readlines())
                app.log.error(err)
            e = Exception("Bootstrap error: {}".format(err))
            return self.__handle_exception(e)

        track_event("Juju Bootstrap", "Done", "")
        EventLoop.remove_alarms()
        app.ui.set_footer('Bootstrap complete...')
        self.__post_bootstrap_exec()

    def __do_bootstrap(self, cloud=None, credential=None):
        """ We call self in two seperate places so add self for clarity
        """
        if cloud is None:
            cloud = self.cloud

        app.log.debug("Performing bootstrap: {} {}".format(
            app.current_controller, cloud))

        app.ui.set_footer('Bootstrapping Juju controller in the background...')

        future = juju.bootstrap_async(
            controller=app.current_controller,
            cloud=cloud,
            credential=credential,
            exc_cb=self.__handle_exception)
        app.bootstrap.running = future

        future.add_done_callback(
            self.__handle_bootstrap_done)
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
            common.save_creds(self.cloud, credentials)

        credentials_key = common.try_get_creds(self.cloud)

        if self.cloud == 'maas':
            self.cloud = '{}/{}'.format(self.cloud,
                                        credentials['@maas-server'].value)
        utils.pollinate(app.session_id, 'CA')
        self.__do_bootstrap(credential=credentials_key)

    def render(self, cloud):
        """ Render

        Arguments:
        cloud: The cloud to create credentials for
        """
        track_screen("Cloud Creation")
        self.cloud = cloud
        if app.current_controller is None:
            app.current_controller = petname.Name()

        if app.current_model is None:
            app.current_model = 'conjure-up'

        # LXD is a special case as we want to make sure a bridge
        # is configured. If not we'll bring up a new view to allow
        # a user to configure a LXD bridge with suggested network
        # information.

        if self.cloud == 'localhost':
            if not utils.check_bridge_exists():
                return controllers.use('lxdsetup').render()

            app.log.debug("Found an IPv4 address, "
                          "assuming LXD is configured.")

            self.__do_bootstrap()

            return controllers.use('deploy').render()

        # XXX: always prompt for maas information for now as there is no way to
        # logically store the maas server ip for future sessions.
        if common.try_get_creds(self.cloud) \
           is not None and self.cloud != 'maas':
            self.__do_bootstrap(credential=common.try_get_creds(self.cloud))
            return controllers.use('deploy').render()

        # show credentials editor otherwise
        try:
            creds = Schema[self.cloud]
        except KeyError as e:
            track_exception("Credentials Error")
            return app.ui.show_exception_message(e)

        view = NewCloudView(app,
                            self.cloud,
                            creds,
                            self.finish)

        app.ui.set_header(
            title="New cloud setup",
        )
        app.ui.set_body(view)
        app.ui.set_footer("")


_controller_class = NewCloudController
