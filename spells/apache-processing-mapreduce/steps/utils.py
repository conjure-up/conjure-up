from subprocess import run, PIPE
import yaml
import sys
import time

# Conjure-up specific
sys.path.insert(0, '/usr/share/conjure-up/hooklib')
import juju  # noqa
from writer import log, success, fail, error  # noqa


def run_smoke_test(service):
    is_complete = False
    sh = run('juju run-action {}/0 smoke-test'.format(service),
             shell=True,
             stdout=PIPE)
    run_action_output = yaml.load(sh.stdout.decode())
    log.debug("{}: {}".format(sh.args, run_action_output))
    action_id = run_action_output.get('Action queued with id', None)
    log.debug("Found action: {}".format(action_id))
    if not action_id:
        fail("Could not determine action id for smoke-test")

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
            fail("The smoke-test failed, "
                 "please have a look at `juju show-action-status`")
        if output['status'] == 'completed':
            completed_msg = "{} smoke-test passed".format(service)
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
    fail("There is an unknown issue with running the smoke-test, "
         "please have a look at `juju show-action-status`")
