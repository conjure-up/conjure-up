from . import common
from collections import deque
from conjure import juju
from conjure import utils
from conjure.api.models import model_info
from conjure.app_config import app
from glob import glob
from subprocess import CalledProcessError
import json
import os
import sys
import time


def finish():
    utils.info("Finished.")
    sys.exit(0)


def render():
    info = model_info(app.current_model)
    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']

    bundle = os.path.join(
        app.config['spell-dir'], 'bundle.yaml')
    bundle_scripts = os.path.join(
        app.config['spell-dir'], 'conjure/steps'
    )

    pre_exec_sh = os.path.join(bundle_scripts, '00_pre.sh')

    # Pre processing
    if os.path.isfile(pre_exec_sh) \
       and os.access(pre_exec_sh, os.X_OK):
        utils.info("Setting up prerequisites")
        try:
            sh = common.run_script(pre_exec_sh)
            if sh.returncode > 0:
                raise Exception(
                    "Cannot execute pre-processing script: {}".format(
                        sh.stderr.decode('utf8')))
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
    steps_queue = deque()
    for step in steps:
        if "00_pre.sh" in step or "00_post-bootstrap.sh" in step:
            app.log.debug("Skipping pre and post-bootstrap steps.")
            continue

        if os.access(step, os.X_OK):
            steps_queue.append(step)

    is_requeued = False
    while steps_queue:
        step = steps_queue.popleft()
        if not is_requeued:
            utils.info(
                "Running: {}".format(common.parse_description(step)))
        sh = common.run_script(step)
        result = json.loads(sh.stdout.decode('utf8'))
        if result['returnCode'] > 0:
            utils.error(
                "Failure in step: {}".format(result['message']))
            sys.exit(1)
        if not result['isComplete']:
            time.sleep(5)
            if not is_requeued:
                utils.warning("{}, please wait".format(
                    result['message']))
            steps_queue.appendleft(step)
            is_requeued = True
            continue
        utils.info(result['message'])
        is_requeued = False
        app.log.debug("post execution done: {}".format(result))
    finish()
