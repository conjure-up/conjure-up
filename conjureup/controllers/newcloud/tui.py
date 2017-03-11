import json
import os
import sys
from subprocess import PIPE

from conjureup import controllers, juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app

from . import common


class NewCloudController:

    def do_post_bootstrap(self):
        """ runs post bootstrap script if exists
        """
        # Set provider type for post-bootstrap
        app.env['JUJU_PROVIDERTYPE'] = model_info().provider_type
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model

        post_bootstrap_sh = os.path.join(app.config['spell-dir'],
                                         'steps/00_post-bootstrap')
        if os.path.isfile(post_bootstrap_sh) \
           and os.access(post_bootstrap_sh, os.X_OK):
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

    def render(self):
        cloud = juju.get_cloud(app.current_cloud)
        if cloud['type'] != 'lxd':
            if not common.try_get_creds(app.current_cloud):
                utils.warning("You attempted to do an install against a cloud "
                              "that requires credentials that could not be "
                              "found.  If you wish to supply those "
                              "credentials please run "
                              "`juju add-credential "
                              "{}`.".format(app.current_cloud))
                sys.exit(1)

        if cloud['type'] == 'lxd':
            common.is_lxd_ready()

        utils.info("Bootstrapping Juju controller \"{}\" "
                   "with deployment \"{}\"".format(
                       app.current_controller,
                       app.current_model))
        p = juju.bootstrap(controller=app.current_controller,
                           cloud=app.current_cloud,
                           model=app.current_model,
                           credential=common.try_get_creds(app.current_cloud))
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
