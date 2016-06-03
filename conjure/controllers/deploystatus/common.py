from subprocess import run, PIPE
from conjure.app_config import app
from collections import Counter
from conjure.api import application


def check_statuses():
    """ verify no errors happen and wait for services to be ready
    """
    statuses = application.get_workload_statuses()
    statuses_threshold = len(statuses) / 2
    counts = Counter(statuses)
    if 'error' in statuses:
        raise Exception(
            'There is an error in one of the charms. Please consult that '
            'charms documentation.')
    # If more than half are active move on to the processing
    if counts['active'] > statuses_threshold:
        return True
    return False


def run_script(path):
    return run(path, shell=True, stderr=PIPE, stdout=PIPE, env=app.env)
