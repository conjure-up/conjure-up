import json
import os
import os.path as path
from glob import glob

import yaml

from conjureup import juju, utils
from conjureup.api.models import model_info
from conjureup.app_config import app
from conjureup.models.step import StepModel


class ValidationError(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(msg, *args, **kwargs)


def set_env(inputs):
    """ Sets the application environment with the key/value from the steps
    input so they can be made available in the step shell scripts
    """
    app.log.debug("Set_env inputs: {}".format(inputs))
    for i in inputs:
        env_key = i['key'].upper()
        try:
            input_key = str(i['input'])
        except KeyError:
            input_key = str(i.get('default', ''))
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


def load_step(step_meta_path):
    step_ex_path, ext = path.splitext(step_meta_path)
    short_path = '/'.join(step_ex_path.split('/')[-3:])
    if not path.isfile(step_ex_path):
        raise ValidationError(
            'Step {} has no implementation'.format(short_path))
    elif not os.access(step_ex_path, os.X_OK):
        raise ValidationError(
            'Step {} is not executable, make sure it has '
            'the executable bit set'.format(short_path))
    with open(step_meta_path) as fp:
        step_metadata = yaml.load(fp.read())
        model = StepModel(step_metadata, step_ex_path)
        return model


def do_step(step_model, step_widget, message_cb, gui=False):
    """ Processes steps in the background

    Arguments:
    step: a step to run
    message_cb: log writer
    gui: optionally set an UI components if GUI

    Returns:
    Step title and results message
    """

    if utils.is_linux() and step_model.needs_sudo:
        password = None
        if step_widget and step_widget.sudo_input:
            password = step_widget.sudo_input.value
        if not step_model.can_sudo(password):
            raise Exception('Sudo failed')

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

    try:
        info = model_info(app.current_model)
    except:
        juju.login(force=True)
        info = model_info(app.current_model)

    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = info['provider-type']

    # Set current juju controller and model
    app.env['JUJU_CONTROLLER'] = app.current_controller
    app.env['JUJU_MODEL'] = app.current_model

    if info['provider-type'] == "maas":
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
