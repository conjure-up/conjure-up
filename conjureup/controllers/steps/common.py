import os
from pathlib import Path

import yaml

from conjureup import utils
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


def get_step_metadata_filenames():
    """Gets a list of step metadata filenames sorted alphabetically
    (hence in execution order)

    Returns:
    list of step metadata file names

    """
    steps_dir = Path(app.config['spell-dir']) / 'steps'
    return sorted(steps_dir.glob('step-*.yaml'))


def load_step(step_meta_path):
    step_meta_path = Path(step_meta_path)
    step_name = step_meta_path.stem
    step_ex_path = step_meta_path.parent / step_name
    if not step_ex_path.is_file():
        raise ValidationError(
            'Step {} has no implementation'.format(step_name))
    elif not os.access(str(step_ex_path), os.X_OK):
        raise ValidationError(
            'Step {} is not executable'.format(step_name))
    step_metadata = yaml.safe_load(step_meta_path.read_text())
    model = StepModel(step_metadata, str(step_ex_path), step_name)
    return model


async def do_step(step_model, msg_cb):
    """ Processes steps in the background

    Arguments:
    step: a step to run
    message_cb: log writer
    gui: optionally set an UI components if GUI

    Returns:
    Step title and results message
    """
    provider_type = app.juju.client.info.provider_type

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

    return await utils.run_step(step_model.name, step_model.title, msg_cb)
