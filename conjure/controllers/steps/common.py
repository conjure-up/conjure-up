from subprocess import run, PIPE
from conjure.app_config import app


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
