from .common import run_script
from conjure.app_config import app
from conjure import utils
from conjure import juju
from subprocess import CalledProcessError
import json
import os
import sys


def finish():
    utils.info("Finished.")
    sys.exit(0)


def render():
    bundle = os.path.join(
        app.config['metadata']['spell-dir'], 'bundle.yaml')
    bundle_scripts = os.path.join(
        app.config['metadata']['spell-dir'], 'conjure/scripts'
    )

    pre_exec_sh = os.path.join(bundle_scripts, 'pre.sh')
    post_exec_sh = os.path.join(bundle_scripts, 'post.sh')

    # Pre processing
    if os.path.isfile(pre_exec_sh) \
       and os.access(pre_exec_sh, os.X_OK):
        app.log.debug(
            "Running pre execution script".format(pre_exec_sh))
        try:
            sh = run_script(pre_exec_sh)
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

    # post processing
    if os.path.isfile(post_exec_sh) \
       and os.access(post_exec_sh, os.X_OK):
        app.log.debug(
            "Running post execution script".format(post_exec_sh))
        try:
            sh = run_script(post_exec_sh)
            result = json.loads(sh.stdout.decode('utf8'))
            app.log.debug("post execution done: {}".format(result))
        except CalledProcessError as e:
            utils.warning(
                "Failure in post processor: {}".format(e))
            sys.exit(1)
    finish()
