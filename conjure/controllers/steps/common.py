from subprocess import run, PIPE
from conjure.app_config import app
from conjure.api.models import model_info
import json
import os
from collections import deque
from glob import glob


def run_script(path):
    return run(path, shell=True, stderr=PIPE, stdout=PIPE, env=app.env)


def set_env(inputs):
    """ Sets the application environment with the key/value from the steps
    input so they can be made available in the step shell scripts
    """
    for i in inputs:
        env_key = i['key'].upper()
        app.env[env_key] = i['input']
        app.log.debug("Setting environment var: {}={}".format(
            env_key,
            app.env[env_key]))


def get_steps(steps_dir):
    """ Gets a list of steps that can be executed on

    Arguments:
    steps_dir: path of steps

    Returns:
    list of executable steps
    """
    return deque(sorted(glob(os.path.join(steps_dir, 'step-*.yaml'))))


def do_step(step, message_cb, icon_state=None):
    """ Processes steps in the background

    Arguments:
    step: a step to run
    message_cb: log writer
    icon_state: optionally set an icon state (gui only)

    Returns:
    Step title and results message
    """

    info = model_info(app.current_model)
    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['ProviderType']

    set_env(step.additional_input)

    if not os.access(step.path, os.X_OK):
        app.log.error("Step {} not executable".format(step.path))

    message_cb("Working: {}".format(step.title))
    if icon_state:
        icon_state(step.icon, 'waiting')
    app.log.debug("Executing script: {}".format(step.path))
    sh = run_script(step.path)
    result = json.loads(sh.stdout.decode('utf8'))
    if result['returnCode'] > 0:
        app.log.error(
            "Failure in step: {}".format(result['message']))
        raise Exception(result['message'])
    message_cb("Done: {}".format(step.title))
    step.result = result['message']
    if icon_state:
        icon_state(step.icon, 'active')
    return step
