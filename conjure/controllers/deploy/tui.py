import sys
import os
import json
from functools import partial

from conjure import controllers
from conjure import utils
from conjure.api.models import model_info
from conjure.app_config import app
from conjure import juju
from subprocess import run, PIPE
from .common import get_bundleinfo, get_metadata_controller


this = sys.modules[__name__]
this.bundle_filename = None
this.bundle = None
this.services = []


def __handle_exception(tag, exc):
    utils.error("Error deploying services: {}".format(exc))
    sys.exit(1)


def do_pre_deploy():
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


def finish():
    """ handles deployment

    """
    this.bundle_filename, this.bundle, this.services = get_bundleinfo()
    app.metadata_controller = get_metadata_controller(this.bundle,
                                                      this.bundle_filename)

    for service in this.services:
        juju.deploy_service(service, utils.info,
                            partial(__handle_exception, "ED"))

    f = juju.set_relations(this.services,
                           utils.info,
                           partial(__handle_exception, "ED"))

    utils.pollinate(app.session_id, 'PC')
    controllers.use('deploystatus').render()


def render():
    do_pre_deploy()
    finish()
