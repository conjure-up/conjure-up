from subprocess import run, PIPE
from conjure.app_config import app
from conjure.api.models import model_info
import time
import json
import os
from collections import deque


def __readlines_key(key, data):
    """ reads lines looking for a key

    Arguments:
    key: key to stop on
    data: list of data usually from reading a file
    """
    for line in data:
        if key in line:
            try:
                return line.split(":")[1].strip()
            except:
                pass
    app.log.debug("Unknown Description/Title, "
                  "please check your step file: {}".format(
                      key))
    return ""


def parse_description(step):
    """ Parses description from step file

    Arguments:
    step: path to step file
    """
    app.log.debug("parse_title: {}".format(step))
    with open(step) as fd:
        lines = fd.readlines()

    return __readlines_key('Description:', lines)


def parse_title(step):
    """ Parses title from step file

    Arguments:
    step: path to step file
    """
    app.log.debug("parse_title: {}".format(step))
    with open(step) as fd:
        lines = fd.readlines()

    return __readlines_key('Title:', lines)


def run_script(path):
    return run(path, shell=True, stderr=PIPE, stdout=PIPE, env=app.env)


def wait_for_steps(steps, message_cb, icon_state=None):
    """ Waits for post processing steps and return its results

    Arguments:
    steps: list of steps to run
    message_cb: log writer
    icon_state: optionally set an icon state (gui only)
    """

    info = model_info(app.current_model)
    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']

    results = []
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
            message_cb(
                "Running: {}".format(parse_title(step)))
        sh = run_script(step)
        result = json.loads(sh.stdout.decode('utf8'))
        if result['returnCode'] > 0:
            app.log.error(
                "Failure in step: {}".format(result['message']))
            raise Exception(result['message'])
        elif not result['isComplete']:
            time.sleep(5)
            if not is_requeued:
                message_cb("{}, please wait".format(
                    result['message']))
            if icon_state:
                icon_state(step, 'waiting')
            steps_queue.appendleft(step)
            is_requeued = True
            continue
        else:
            message_cb(result['message'])
            results.append(result['message'])
            if icon_state:
                icon_state(step, 'active')
        is_requeued = False
        app.log.debug("post execution done: {}".format(result))
    return results
