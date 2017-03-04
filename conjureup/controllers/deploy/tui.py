import concurrent
import json
import os
import sys
from functools import partial
from operator import attrgetter
from subprocess import PIPE

from conjureup import controllers, juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app


class DeployController:

    def __init__(self):
        self.bundle_filename = None
        self.bundle = None
        self.applications = []

    def __handle_exception(self, tag, exc):
        utils.error("Error deploying services: {}".format(exc))
        sys.exit(1)

    def do_pre_deploy(self):
        """ runs pre deploy script if exists
        """
        # Set provider type for post-bootstrap
        app.env['JUJU_PROVIDERTYPE'] = model_info().provider_type
        app.env['JUJU_CONTROLLER'] = app.current_controller
        app.env['JUJU_MODEL'] = app.current_model
        app.env['CONJURE_UP_SPELLSDIR'] = app.argv.spells_dir

        pre_deploy_sh = os.path.join(app.config['spell-dir'],
                                     'steps/00_pre-deploy')
        if os.path.isfile(pre_deploy_sh) \
           and os.access(pre_deploy_sh, os.X_OK):
            utils.info("Running pre deployment tasks.")
            try:
                sh = utils.run(pre_deploy_sh, shell=True,
                               stdout=PIPE,
                               stderr=PIPE,
                               env=app.env)
                try:
                    result = json.loads(sh.stdout.decode('utf8'))
                except json.decoder.JSONDecodeError as e:
                    utils.error(sh.stdout.decode())
                    utils.error(sh.stderr.decode())
                    sys.exit(1)
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
        for service in self.applications:
            if app.current_cloud == "localhost":
                service.placement_spec = None
            juju.deploy_service(service,
                                app.metadata_controller.series,
                                utils.info,
                                partial(self.__handle_exception, "ED"))

        f = juju.set_relations(self.applications,
                               utils.info,
                               partial(self.__handle_exception, "ED"))
        concurrent.futures.wait([f])

        controllers.use('deploystatus').render()

    def render(self):
        self.do_pre_deploy()
        juju.add_machines(
            list(app.metadata_controller.bundle.machines.values()),
            exc_cb=partial(self.__handle_exception, "ED"))
        self.applications = sorted(app.metadata_controller.bundle.services,
                                   key=attrgetter('service_name'))

        self.finish()


_controller_class = DeployController
