from subprocess import run, PIPE
from conjure.app_config import app
from subprocess import CalledProcessError
import json
import os
import time


def wait_for_applications(script, msg_cb):
    """ Processes a 00_deploy-done.sh to verify if applications are available

    Arguments:
    script: script to run (00_deploy-done.sh)
    msg_cb: message callback
    """
    if os.path.isfile(script) \
       and os.access(script, os.X_OK):
        msg_cb("Waiting for applications to start")
        try:
            rerun = True
            count = 0
            while rerun:
                sh = run_script(script)
                result = json.loads(sh.stdout.decode('utf8'))
                if result['returnCode'] > 0:
                    app.log.error(
                        "Failure in deploy done: {}".format(result['message']))
                    raise Exception(result['message'])
                if not result['isComplete']:
                    time.sleep(5)
                    if count == 0:
                        msg_cb("{}, please wait".format(
                            result['message']))
                        count += 1
                    continue
                count = 0
                rerun = False
        except CalledProcessError as e:
            raise e


def run_script(path):
    return run(path, shell=True, stderr=PIPE, stdout=PIPE, env=app.env)
