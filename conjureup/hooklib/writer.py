import json
import sys


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
