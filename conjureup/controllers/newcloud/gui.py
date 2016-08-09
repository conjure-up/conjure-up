from . import common
from conjureup import async
from conjureup import controllers
from conjureup import juju
from conjureup import utils
from conjureup.api.models import model_info
from conjureup.app_config import app
from conjureup.models.provider import Schema
from conjureup.ui.views.newcloud import NewCloudView
from functools import partial
from subprocess import check_output
from ubuntui.ev import EventLoop
import json
import os
import os.path as path
import petname


class NewCloudController:
    def __init__(self):
        self.cloud = None

    def __handle_exception(self, exc):
        utils.pollinate(app.session_id, 'EB')
        return app.ui.show_exception_message(exc)

    def __handle_bootstrap_done(self, future):
        app.log.debug("handle bootstrap")
        result = future.result()
        if result.returncode < 0:
            # bootstrap killed via user signal, we're quitting
            return
        if result.returncode > 0:
            err = result.stderr.read().decode()
            app.log.error(err)
            return self.__handle_exception(Exception("error "))

        utils.pollinate(app.session_id, 'J004')
        EventLoop.remove_alarms()
        app.ui.set_footer('Bootstrap complete...')
        juju.switch_controller(app.current_controller)
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

    def __post_bootstrap_exec(self):
        """ Executes post-bootstrap.sh if exists
        """
        info = model_info(juju.get_current_model())
        # Set our provider type environment var so that it is
        # exposed in future processing tasks
        app.env['JUJU_PROVIDERTYPE'] = info['provider-type']

        _post_bootstrap_sh = path.join(app.config['spell-dir'],
                                       'conjure/steps/00_post-bootstrap')
        app.log.debug(
            'Checking for post bootstrap task: {}'.format(_post_bootstrap_sh))
        if path.isfile(_post_bootstrap_sh) \
           and os.access(_post_bootstrap_sh, os.X_OK):
            app.ui.set_footer('Running post-bootstrap tasks...')
            utils.pollinate(app.session_id, 'J001')
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
            utils.pollinate(app.session_id, 'E001')
            return self.__handle_exception(Exception(
                'There was an error during the post '
                'bootstrap processing phase: {}.'.format(result)))
        utils.pollinate(app.session_id, 'J002')
        app.ui.set_footer('')
        app.log.debug("Switching to controller: {}".format(
            app.current_controller))
        juju.switch_controller(app.current_controller)
        controllers.use('bundlereadme').render()

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

        return controllers.use('bundlereadme').render()

    def render(self, cloud):
        """ Render

        Arguments:
        cloud: The cloud to create credentials for
        """

        self.cloud = cloud
        if app.current_controller is None:
            app.current_controller = petname.Name()

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

            return controllers.use('bundlereadme').render()

        # XXX: always prompt for maas information for now as there is no way to
        # logically store the maas server ip for future sessions.
        if common.try_get_creds(self.cloud) \
           is not None and self.cloud != 'maas':
            self.__do_bootstrap(credential=common.try_get_creds(self.cloud))
            return controllers.use('bundlereadme').render()

        # show credentials editor otherwise
        try:
            creds = Schema[self.cloud]
        except KeyError as e:
            utils.pollinate(app.session_id, 'EC')
            return app.ui.show_exception_message(e)

        view = NewCloudView(app,
                            self.cloud,
                            creds,
                            self.finish)

        app.ui.set_header(
            title="New cloud setup",
        )
        app.ui.set_body(view)


_controller_class = NewCloudController
