from conjure.app_config import app
from conjure.api.models import model_info
from conjure import utils
import json
import os
from collections import deque
from glob import glob


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


def do_step(step, message_cb, gui=False):
    """ Processes steps in the background

    Arguments:
    step: a step to run
    message_cb: log writer
    gui: optionally set an UI components if GUI

    Returns:
    Step title and results message
    """

    step.clear_button()

    # merge the step_widget input data into our step model
    for i in step.model.additional_input:
        try:
            matching_widget = [
                x for x in step.widget.additional_input
                if x['key'] == i['key']][0]
            i['input'] = matching_widget['input'].value
        except IndexError as e:
            app.log.error(
                "Tried to pull a value from an "
                "invalid input: {}/{}".format(e,
                                              matching_widget))

    info = model_info(app.current_model)
    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['provider-type']

    set_env(step.model.additional_input)

    if not os.access(step.model.path, os.X_OK):
        app.log.error("Step {} not executable".format(step.model.path))

    message_cb("Working: {}".format(step.model.title))
    if gui:
        step.set_icon_state('waiting')
    app.log.debug("Executing script: {}".format(step.model.path))
    sh = utils.run_script(step.model.path)
    result = json.loads(sh.stdout.decode('utf8'))
    if result['returnCode'] > 0:
        app.log.error(
            "Failure in step: {}".format(result['message']))
        raise Exception(result['message'])
    message_cb("Done: {}".format(step.model.title))
    step.model.result = result['message']
    if gui:
        step.set_icon_state('active')
        step.set_description(
            "{}\n\nResult: {}".format(
                step.model.description,
                step.model.result),
            'info_context')
    return step
