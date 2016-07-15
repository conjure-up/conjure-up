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


def update_icon_state(icon, result_code):
    """ updates status icon

    Arguments:
    icon: icon widget
    result_code: 3 types of results, error, waiting, complete
    """
    if result_code == "error":
        icon.set_text(
            ("error_icon", "\N{BLACK FLAG}"))
    elif result_code == "waiting":
        icon.set_text(("pending_icon", "\N{HOURGLASS}"))
    elif result_code == "active":
        icon.set_text(("success_icon", "\N{BALLOT BOX WITH CHECK}"))
    else:
        # NOTE: Should not get here, if we do make sure we account
        # for that error type above.
        icon.set_text(("error_icon", "?"))


def do_step(step, message_cb, gui=False):
    """ Processes steps in the background

    Arguments:
    step: a step to run
    message_cb: log writer
    gui: optionally set an UI components if GUI

    Returns:
    Step title and results message
    """

    info = model_info(app.current_model)
    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['provider-type']

    set_env(step.additional_input)

    if not os.access(step.path, os.X_OK):
        app.log.error("Step {} not executable".format(step.path))

    message_cb("Working: {}".format(step.title))
    if gui:
        update_icon_state(step.widget.icon, 'waiting')
    app.log.debug("Executing script: {}".format(step.path))
    sh = utils.run_script(step.path)
    result = json.loads(sh.stdout.decode('utf8'))
    if result['returnCode'] > 0:
        app.log.error(
            "Failure in step: {}".format(result['message']))
        raise Exception(result['message'])
    message_cb("Done: {}".format(step.title))
    step.result = result['message']
    if gui:
        # All is well here, set the current title and description back
        # to a darker color and set the next widget to a bright white
        # if exists.
        update_icon_state(step.widget.icon, 'active')
        step.widget.description.set_text((
            'info_context', "{}\n\nResult: {}".format(
                step.widget.description.get_text()[0],
                step.result)))
        if step.next_widget:
            step.next_widget.description.set_text(
                ('body',
                 step.next_widget.description.get_text()[0]))
            for i in step.widget.additional_input:
                i['label'].set_text(('info_minor',
                                     i['label'].get_text()[0]))
            for i in step.next_widget.additional_input:
                i['label'].set_text(('body', i['label'].get_text()[0]))
    return step
