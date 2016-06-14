from subprocess import run, PIPE, CalledProcessError
import yaml


def status():
    """ Get juju status
    """
    try:
        sh = run('juju status --format yaml', shell=True, check=True,
                 stdout=PIPE)
    except CalledProcessError:
        return None
    return yaml.load(sh.stdout.decode())


def leader(application):
    """ Grabs the leader of a set of application units

    Arguments:
    application: name of application to query.
    """
    try:
        sh = run('juju run --application $1 is-leader --format yaml',
                 shell=True, stdout=PIPE, check=True)
    except CalledProcessError:
        return None

    leader_yaml = yaml.load(sh.stdout.decode())

    for leader in leader_yaml:
        if leader['Stdout'].strip() == 'True':
            return leader['UnitId']
