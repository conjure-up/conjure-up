import logging
from logging.handlers import SysLogHandler
import os
import json
import sys


def _setup_logging(app, debug=True):
    cmdslog = SysLogHandler('/dev/log',
                            facility=SysLogHandler.LOG_DAEMON)
    if debug:
        env = logging.DEBUG
        cmdslog.setFormatter(logging.Formatter(
            "%(name)s: [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"))
    else:
        env = logging.INFO
        cmdslog.setFormatter(logging.Formatter(
            "%(name)s: [%(levelname)s] %(message)s"))

    cmdslog.setLevel(env)

    logger = logging.getLogger(app)
    logger.setLevel(env)
    logger.addHandler(cmdslog)
    return logger


env = os.environ.get('CONJURE_UP_SPELL', 'unknown-spell')
log = _setup_logging('conjure-up/{}'.format(env))


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
