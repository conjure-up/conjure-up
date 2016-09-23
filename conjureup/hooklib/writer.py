import json
import os
import sys

from conjureup.log import setup_logging

CACHEDIR = os.getenv('CONJURE_UP_CACHEDIR',
                     os.path.expanduser('~/.cache/conjure-up'))
SPELL_NAME = os.getenv('CONJURE_UP_SPELL', '_unspecified_spell')
LOGFILE = os.path.join(CACHEDIR, '{spell}.log'.format(spell=SPELL_NAME))

log = setup_logging("conjure-up/{}".format(SPELL_NAME), LOGFILE, True)


def success(msg):
    """ Returns a successful step
    """
    print(json.dumps({
        'message': msg,
        'returnCode': 0,
        'isComplete': True
    }))
    sys.exit(0)


def fail(msg):
    """ Logs a failed step, does not stop step execution
    """
    print(json.dumps({
        'message': msg,
        'returnCode': 0,
        'isComplete': False
    }))
    sys.exit(0)


def error(msg):
    """ Logs a fatal error, does stop step execution
    """
    print(json.dumps({
        'message': msg,
        'returnCode': 1,
        'isComplete': False
    }))
    sys.exit(0)


def info(msg):
    print(json.dumps({
        'message': msg}))
    sys.stdout.flush()
