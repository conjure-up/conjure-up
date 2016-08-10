from subprocess import run, PIPE, CalledProcessError
import yaml
import logging
import time
from .writer import fail, success
log = logging.getLogger('conjureup')


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
        sh = run(
            'juju run --application {} is-leader --format yaml'.format(
                application),
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


def run_action(unit, action):
    """ runs an action on a unit, waits for result
    """
    is_complete = False
    sh = run('juju run-action {} {}'.format(unit, action),
             shell=True,
             stdout=PIPE)
    run_action_output = yaml.load(sh.stdout.decode())
    log.debug("{}: {}".format(sh.args, run_action_output))
    action_id = run_action_output.get('Action queued with id', None)
    log.debug("Found action: {}".format(action_id))
    if not action_id:
        fail("Could not determine action id for test")

    while not is_complete:
        sh = run('juju show-action-output {}'.format(action_id),
                 shell=True,
                 stderr=PIPE,
                 stdout=PIPE)
        log.debug(sh)
        try:
            output = yaml.load(sh.stdout.decode())
            log.debug(output)
        except Exception as e:
            log.debug(e)
        if output['status'] == 'running' or output['status'] == 'pending':
            time.sleep(5)
            continue
        if output['status'] == 'failed':
            fail("The test failed, "
                 "please have a look at `juju show-action-status`")
        if output['status'] == 'completed':
            completed_msg = "{} test passed".format(unit)
            results = output.get('results', None)
            if not results:
                is_complete = True
                success(completed_msg)
            if results.get('outcome', None):
                is_complete = True
                completed_msg = "{}: (result) {}".format(
                    completed_msg,
                    results.get('outcome'))
                success(completed_msg)
    fail("There is an unknown issue with running the test, "
         "please have a look at `juju show-action-status`")
