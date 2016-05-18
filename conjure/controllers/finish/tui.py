from . import common
from conjure.app_config import app
from conjure import utils
from conjure import juju
from subprocess import CalledProcessError
import json
import os
import sys
from glob import glob


def finish():
    utils.info("Finished.")
    sys.exit(0)


def render():
    bundle = os.path.join(
        app.config['metadata']['spell-dir'], 'bundle.yaml')
    bundle_scripts = os.path.join(
        app.config['metadata']['spell-dir'], 'conjure/steps'
    )

    pre_exec_sh = os.path.join(bundle_scripts, '00_pre.sh')

    # Pre processing
    if os.path.isfile(pre_exec_sh) \
       and os.access(pre_exec_sh, os.X_OK):
        utils.info("Setting up prerequisites")
        try:
            sh = common.run_script(pre_exec_sh)
            result = json.loads(sh.stdout.decode('utf8'))
            app.log.debug("pre execution done: {}".format(result))
        except CalledProcessError as e:
            utils.warning(
                "Failure in pre processor: {}".format(e))
            sys.exit(1)

    # juju deploy
    try:
        utils.info("Deploying charms")
        juju.deploy(bundle)
    except Exception as e:
        utils.error("Problem with deployment: {}".format(e))
        sys.exit(1)

    # post step processing
    steps = sorted(glob(os.path.join(bundle_scripts, '*.sh')))
    for step in steps:
        if "00_pre.sh" in step or "00_post-bootstrap.sh" in step:
            app.log.debug("Skipping pre and post-bootstrap steps.")
            continue

        if os.access(step, os.X_OK):
            utils.info(
                "Running {}".format(common.parse_description(step)))
        try:
            sh = common.run_script(step)
            result = json.loads(sh.stdout.decode('utf8'))
            app.log.debug("post execution done: {}".format(result))
        except CalledProcessError as e:
            utils.warning(
                "Failure in step: {}".format(e))
            sys.exit(1)
    finish()
