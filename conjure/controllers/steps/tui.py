from . import common
from collections import deque
from conjure import utils
from conjure.app_config import app
from glob import glob
import json
import os
import sys
import time


def finish():
    # return controllers.use('summary').render()
    utils.info("Finished.")
    sys.exit(0)


def render():
    bundle_scripts = os.path.join(
        app.config['spell-dir'], 'conjure/steps'
    )

    # post step processing
    steps = sorted(glob(os.path.join(bundle_scripts, '*.sh')))
    steps_queue = deque()
    for step in steps:
        if "00_pre.sh" in step \
           or "00_post-bootstrap.sh" in step \
           or "00_deploy-done.sh" in step:
            app.log.debug("Skipping non steps.")
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
