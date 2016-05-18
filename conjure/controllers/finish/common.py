from subprocess import run, PIPE
from conjure.app_config import app


def parse_description(step):
    """ Parses description from step file

    Arguments:
    step: path to step file
    """
    with open(step) as fd:
        lines = fd.readlines()

    for line in lines:
        if "Description:" in line:
            try:
                return line.split(":")[1].strip()
            except:
                return "Unknown Description, please check your step file"
    return "Unknown Description, please check your step file"


def run_script(path):
    return run(path, shell=True, stderr=PIPE, stdout=PIPE, env=app.env)
