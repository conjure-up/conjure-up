import json
import os
from glob import glob

from conjureup import utils
from conjureup.api.models import model_info
from conjureup.app_config import app


def set_env(inputs):
    """ Sets the application environment with the key/value from the steps
    input so they can be made available in the step shell scripts
    """
    app.log.debug("Set_env inputs: {}".format(inputs))
    for i in inputs:
        env_key = i['key'].upper()
        try:
            input_key = i['input']
        except KeyError:
            input_key = i.get('default', '')
        app.env[env_key] = input_key
        app.log.debug("Setting environment var: {}={}".format(
            env_key,
            app.env[env_key]))


def get_step_metadata_filenames(steps_dir):
    """Gets a list of step metadata filenames sorted alphabetically
    (hence in execution order)

    Arguments:
    steps_dir: path to search for step metadata files

    Returns:
    list of step metadata file names

    """
    return sorted(glob(os.path.join(steps_dir, 'step-*.yaml')))


def do_step(step_model, step_widget, message_cb, gui=False):
    """ Processes steps in the background

    Arguments:
    step: a step to run
    message_cb: log writer
    gui: optionally set an UI components if GUI

    Returns:
    Step title and results message
    """

    # merge the step_widget input data into our step model
    if gui:
        step_widget.clear_button()
        for i in step_model.additional_input:
            try:
                matching_widget = [
                    x for x in step_widget.additional_input
                    if x['key'] == i['key']][0]
                i['input'] = matching_widget['input'].value
            except IndexError as e:
                app.log.error(
                    "Tried to pull a value from an "
                    "invalid input: {}/{}".format(e,
                                                  matching_widget))

    provider_type = model_info().provider_type

    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = provider_type

    # Set current juju controller and model
    app.env['JUJU_CONTROLLER'] = app.current_controller
    app.env['JUJU_MODEL'] = app.current_model

    if provider_type == "maas":
        app.log.debug("MAAS CONFIG: {}".format(app.maas))

        # Expose MAAS endpoints and tokens
        app.env['MAAS_ENDPOINT'] = app.maas.endpoint
        app.env['MAAS_APIKEY'] = app.maas.api_key

    # Set environment variables so they can be accessed from the step scripts
    set_env(step_model.additional_input)

    if not os.access(step_model.path, os.X_OK):
        app.log.error("Step {} not executable".format(step_model.path))

    message_cb("Running step: {}".format(step_model.title))
    if gui:
        step_widget.set_icon_state('waiting')
    app.log.debug("Executing script: {}".format(step_model.path))
    with open(step_model.path + ".out", 'w') as outf:
        with open(step_model.path + ".err", 'w') as errf:
            utils.run_script(step_model.path,
                             stderr=errf,
                             stdout=outf)
    try:
        with open(step_model.path + ".out") as outf:
            lines = outf.readlines()
            try:
                result = json.loads(lines[-1])
            except json.decoder.JSONDecodeError as e:
                raise Exception(
                    "Unable to parse json ({}): {}".format(e, lines))
    except:
        raise Exception("Could not read output from step "
                        "{}: {}".format(step_model.path, lines))
    if 'returnCode' not in result:
        raise Exception("Invalid last message from step: {}".format(result))
    if result['returnCode'] > 0:
        app.log.error(
            "Failure in step: {}".format(result['message']))
        raise Exception(result['message'])

    step_model.result = result['message']
    message_cb("{} completed.".format(step_model.title))

    return (step_model, step_widget)
