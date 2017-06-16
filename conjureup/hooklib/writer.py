import os
import sys

from conjureup.app_config import app
from conjureup.log import setup_logging

CACHEDIR = os.getenv('CONJURE_UP_CACHEDIR',
                     os.path.expanduser('~/.cache/conjure-up'))
SPELL_NAME = os.getenv('CONJURE_UP_SPELL', '_unspecified_spell')
LOGFILE = os.path.join(CACHEDIR, '{spell}.log'.format(spell=SPELL_NAME))

app.config = {'metadata': None,
              'spell': SPELL_NAME}
log = setup_logging(app, LOGFILE, True)


def success(msg):
    """ Returns a successful step
    """
    print(msg)
    sys.exit(0)


def fail(msg):
    """ Logs a failed step, does stop step execution
    """
    print(msg)
    sys.exit(1)


def error(msg):
    """ Logs a fatal error, does stop step execution
    """
    print(msg)
    sys.exit(1)


def info(msg):
    print(msg)
    sys.stdout.flush()
