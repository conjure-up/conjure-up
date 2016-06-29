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


def agent_states():
    """ get a list of running agent states

    Returns:
    A list of tuples of [(unit_name, current_state, workload_message)]
    """
    juju_status = status()
    agent_states = []
    for app_name, app_dict in juju_status['applications'].items():
        for unit_name, unit_dict in app_dict.get('units', {}).items():
            cur_state = unit_dict['workload-status']['current']
            message = unit_dict['workload-status'].get(
                'message',
                'Unknown workload status message')
            agent_states.append((unit_name, cur_state, message))
    return agent_states


def machine_states():
    """ get a list of machine states

    Returns:
    A list of tuples of [(machine_name, current_state, machine_message)]
    """
    return [(name, md['juju-status'].get('current', ''),
             md['juju-status'].get('message', ''))
            for name, md in status().get('machines',  {}).items()]
