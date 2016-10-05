import json
import os
import sys
from subprocess import PIPE

import petname

from conjureup import controllers, juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app

from . import common


class NewCloudController:

    def __init__(self):
        self.cloud = None

    def do_post_bootstrap(self):
        """ runs post bootstrap script if exists
        """
        # Set provider type for post-bootstrap
        info = model_info(app.current_model)
        app.env['JUJU_PROVIDERTYPE'] = info['provider-type']
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model

        post_bootstrap_sh = os.path.join(app.config['spell-dir'],
                                         'steps/00_post-bootstrap')
        if os.path.isfile(post_bootstrap_sh) \
           and os.access(post_bootstrap_sh, os.X_OK):
            utils.pollinate(app.session_id, 'J001')
            utils.info("Running post-bootstrap tasks.")
            try:
                sh = utils.run(post_bootstrap_sh, shell=True,
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
            app.current_model = 'conjure-up'

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
        p = juju.bootstrap(controller=app.current_controller,
                           cloud=self.cloud,
                           credential=common.try_get_creds(self.cloud))
        if p.returncode != 0:
            pathbase = os.path.join(
                app.config['spell-dir'],
                '{}-bootstrap').format(app.current_controller)
            with open(pathbase + ".err") as errf:
                utils.error("Error bootstrapping controller: "
                            "{}".format("".join(errf.readlines())))
            sys.exit(1)

        self.do_post_bootstrap()
        self.finish()

_controller_class = NewCloudController
