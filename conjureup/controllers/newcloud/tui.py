from conjureup import controllers
from conjureup import utils
from conjureup.api.models import model_info
from conjureup import juju
from conjureup.app_config import app
from . import common
from subprocess import run, PIPE
import json
import os
import sys
import petname


class NewCloudController:
    def __init__(self):
        self.cloud = None

    def do_post_bootstrap(self):
        """ runs post bootstrap script if exists
        """
        # Set provider type for post-bootstrap
        app.env['JUJU_PROVIDERTYPE'] = model_info('default')['provider-type']

        post_bootstrap_sh = os.path.join(app.config['spell-dir'],
                                         'conjure/steps/00_post-bootstrap')
        if os.path.isfile(post_bootstrap_sh) \
           and os.access(post_bootstrap_sh, os.X_OK):
            utils.pollinate(app.session_id, 'J001')
            utils.info("Running post-bootstrap tasks.")
            try:
                sh = run(post_bootstrap_sh, shell=True,
                         stdout=PIPE,
                         stderr=PIPE,
                         env=app.env)
                result = json.loads(sh.stdout.decode('utf8'))
                utils.info("Finished post bootstrap task: {}".format(
                    result['message']))
            except Exception as e:
                utils.warning(
                    "Failed to run post bootstrap task: {}".format(e))
                sys.exit(1)

    def finish(self):
        return controllers.use('deploy').render()

    def render(self, cloud):

        self.cloud = cloud
        if app.current_controller is None:
            app.current_controller = petname.Name()

        if app.current_model is None:
            app.current_model = 'default'

        if self.cloud != 'localhost':
            if not common.try_get_creds(self.cloud):
                utils.warning("You attempted to do an install against a cloud "
                              "that requires credentials that could not be "
                              "found.  If you wish to supply those "
                              "credentials please run "
                              "`juju add-credential {}`.".format(self.cloud))
                sys.exit(1)

        if self.cloud == 'localhost':
            if not utils.check_bridge_exists():
                return controllers.use('lxdsetup').render()

            app.log.debug("Found an IPv4 address, "
                          "assuming LXD is configured.")

        utils.info("Bootstrapping Juju controller")
        juju.bootstrap(controller=app.current_controller,
                       cloud=self.cloud,
                       credential=common.try_get_creds(self.cloud))
        self.do_post_bootstrap()
        self.finish()

_controller_class = NewCloudController
