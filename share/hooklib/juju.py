from subprocess import run, PIPE
import yaml


def status():
    """ Get juju status
    """
    sh = run('juju status --format yaml', shell=True, stdout=PIPE)
    return yaml.load(sh.stdout.decode())


def leader(application):
    """ Grabs the leader of a set of application units

    Arguments:
    application: name of application to query.
    """
    sh = run('juju run --application $1 is-leader --format yaml',
             shell=True, stdout=PIPE)
    leader_yaml = yaml.load(sh.stdout.decode())

    for leader in leader_yaml:
        if leader['Stdout'].strip() == 'True':
            return leader['UnitId']
