import json
import sys
import logging
import os
try:
    from systemd.journal import JournalHandler
except ImportError:
    from systemd.journal import JournalLogHandler as JournalHandler


def log(msg, level='DEBUG'):
    """ Provides a logging mechanism for spell steps to write to journald
    """
    spell_name = os.getenv('CONJURE_UP_SPELL', '_unspecified_spell')
    logger = logging.getLogger('conjure-up/{}'.format(spell_name))
    level_num = logging.getLevelName(level.upper())

    logger.setLevel(level_num)
    logger.addHandler(JournalHandler(
        SYSLOG_IDENTIFIER='conjure-up/{}'.format(spell_name)))
    logger.log(level_num, msg)


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
