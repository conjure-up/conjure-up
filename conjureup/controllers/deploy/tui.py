import sys
import os
import json
import concurrent
from functools import partial

from conjureup import controllers
from conjureup import utils
from conjureup.api.models import model_info
from conjureup.app_config import app
from conjureup import juju
from subprocess import run, PIPE


class DeployController:
    def __init__(self):
        self.bundle_filename = None
        self.bundle = None
        self.services = []

    def __handle_exception(self, tag, exc):
        utils.error("Error deploying services: {}".format(exc))
        sys.exit(1)

    def do_pre_deploy(self):
        """ runs pre deploy script if exists
        """
        # Set provider type for post-bootstrap
        app.env['JUJU_PROVIDERTYPE'] = model_info('default')['provider-type']

        pre_deploy_sh = os.path.join(app.config['spell-dir'],
                                     'conjure/steps/00_pre-deploy')
        if os.path.isfile(pre_deploy_sh) \
           and os.access(pre_deploy_sh, os.X_OK):
            utils.pollinate(app.session_id, 'J001')
            utils.info("Running pre deployment tasks.")
            try:
                sh = run(pre_deploy_sh, shell=True,
                         stdout=PIPE,
                         stderr=PIPE,
                         env=app.env)
                result = json.loads(sh.stdout.decode('utf8'))
                if result['returnCode'] > 0:
                    utils.error("Failed to run pre-deploy task: "
                                "{}".format(result['message']))
                    sys.exit(1)

                utils.info("Finished pre deploy task: {}".format(
                    result['message']))
            except Exception as e:
                utils.error(
                    "Failed to run pre deploy task: {}".format(e))
                sys.exit(1)

    def finish(self):
        """ handles deployment
        """
        for service in self.services:
            juju.deploy_service(service, utils.info,
                                partial(self.__handle_exception, "ED"))

        f = juju.set_relations(self.services,
                               utils.info,
                               partial(self.__handle_exception, "ED"))
        concurrent.futures.wait([f])

        utils.pollinate(app.session_id, 'PC')
        controllers.use('deploystatus').render()

    def render(self):
        self.do_pre_deploy()
        juju.add_machines(
            list(app.metadata_controller.bundle.machines.values()),
            exc_cb=partial(self.__handle_exception, "ED"))
        self.finish()

_controller_class = DeployController
