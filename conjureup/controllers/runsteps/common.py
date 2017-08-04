from pathlib import Path

from conjureup import utils
from conjureup.app_config import app


def set_env(step_model):
    """ Sets the application environment with the key/value from the steps
    input so they can be made available in the step shell scripts
    """
    step_data = app.steps_data[step_model.name]
    for key, value in step_data.items():
        env_key = key.upper()
        value = step_data[key]
        app.env[env_key] = value
        app.log.info("Setting environment var: {}={}".format(env_key, value))


async def do_step(step_model, msg_cb):
    """ Processes steps in the background

    Arguments:
    step_model: a step to run
    message_cb: log writer
    gui: optionally set an UI components if GUI

    Returns:
    Step title and results message
    """
    provider_type = app.juju.client.info.provider_type

    # Set our provider type environment var so that it is
    # exposed in future processing tasks
    app.env['JUJU_PROVIDERTYPE'] = provider_type

    # Set current credential name (localhost doesn't have one)
    app.env['JUJU_CREDENTIAL'] = app.provider.credential or ''

    # Set current juju controller and model
    app.env['JUJU_CONTROLLER'] = app.provider.controller
    app.env['JUJU_MODEL'] = app.provider.model

    if provider_type == "maas":
        app.log.debug("MAAS CONFIG: {}".format(app.maas))

        # Expose MAAS endpoints and tokens
        app.env['MAAS_ENDPOINT'] = app.maas.endpoint
        app.env['MAAS_APIKEY'] = app.maas.api_key

    # Set environment variables so they can be accessed from the step scripts
    set_env(step_model)

    return await utils.run_step(step_model, msg_cb)


def save_step_results():
    results_file = Path(app.config['spell-dir']) / 'results.txt'
    results_file.write_text(''.join([
        "{}: {}\n".format(step.title, step.result) for step in app.steps
    ]))
