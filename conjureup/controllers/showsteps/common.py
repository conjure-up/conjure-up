import os
from pathlib import Path

import yaml

from conjureup.app_config import app
from conjureup.models.step import StepModel


class ValidationError(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(msg, *args, **kwargs)


def get_step_metadata_filenames():
    """Gets a list of step metadata filenames sorted alphabetically
    (hence in execution order)

    Returns:
    list of step metadata file names

    """
    steps_dir = Path(app.config['spell-dir']) / 'steps'
    return sorted(steps_dir.glob('step-*.yaml'))


def get_addon_metadata_filenames():
    """ Gets a list of selected addons filenames
    """
    steps = []
    for addon in app.addons:
        steps_dir = Path(app.config['spell-dir']) / 'addons' / addon / 'steps'
        steps.extend(sorted(steps_dir.glob('step-*.yaml')))
    return steps


def load_steps():
    """
    Load all step models into app.steps and
    populate app.steps_data, if not already.
    """
    step_filenames = get_step_metadata_filenames() + \
        get_addon_metadata_filenames()
    app.steps = []
    for step_meta_path in step_filenames:
        step = load_step(step_meta_path)
        app.steps.append(step)
        step_data = app.steps_data.get(step.name, {})
        for field in step.additional_input:
            key = field['key']
            default = field.get('default')
            value = step_data.get(key, default)
            step_data[key] = value
        app.steps_data[step.name] = step_data


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
    step_metadata = yaml.load(step_meta_path.read_text())
    model = StepModel(step_metadata, str(step_ex_path), step_name)
    return model
